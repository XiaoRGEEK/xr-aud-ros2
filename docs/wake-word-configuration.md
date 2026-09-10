# 唤醒词配置

## 1. 当前范围

公开接口允许配置多条唤醒短语，但配置词条不等于替换声学模型。当前 wake producer
仍是受控的 Stage 1 DEV 部署。配置只有在系统已经按照离线 Release 安装兼容且获
授权的 KWS backend/model，并启用对应 Stage 1 profile 时才会生效。

模型资源不进入本公开仓库、公开 DEB 仓或系统镜像。已授权的内部/评估用户应通过
既有产品或支持渠道联系 XRGEEK 获取 **XR-AUD-02 DEV v0.2.0** 离线包及其配置
说明。仅克隆本仓库或创建 TSV 不会产生唤醒事件。

## 2. 文件格式

参考 [`config/keywords.tsv.example`](../config/keywords.tsv.example)。文件必须是
UTF-8 TSV，真正的分隔符是 Tab，而不是空格或两个字符 `\t`：

```text
xraudio-stage1-keywords-v1<TAB>generation<TAB>config-id
id<TAB>显示文字<TAB>模型 tokens<TAB>boost<TAB>decoder threshold<TAB>true|false
```

约束：

- 文件最大 64 KiB；
- 单行最大 4096 字节；
- 最多 32 条结构记录，但这是解析安全上限，不是性能、时延或识别率承诺；
- `id` 必须唯一，至少一条记录启用；
- `boost` 留空表示 backend 默认值，否则必须大于 0；
- `decoder threshold` 留空表示 backend 默认值，否则必须在 0..1；
- `generation` 必须比当前已接受配置更大；
- 整份候选文件验证通过后才替换当前配置，部分有效不会部分生效。

## 3. 生成一个具有真实 Tab 的候选文件

先从设备当前配置或离线 Release 记录读取 generation，把下面的 `2` 改成严格更大的
整数。`MODEL_TOKEN_SEQUENCE_FROM_PROVIDER` 必须替换为当前模型和 tokenizer 要求的
真实 token 序列；不能把显示文字直接当作模型 tokens。

以下 `printf` 中的 `\t` 会被 shell 写成真正的 Tab：

```bash
generation=2
candidate=/tmp/xraudio-stage1-keywords.tsv

{
  printf 'xraudio-stage1-keywords-v1\t%s\t%s\n' \
    "$generation" 'site-keywords-v2'
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    'wake_primary' '小瑞小瑞' 'MODEL_TOKEN_SEQUENCE_FROM_PROVIDER' '' '' 'true'
} > "$candidate"
```

增加词条时，每条再写一行六字段记录，并确保 ID 唯一。任意文字并不天然受当前模型
支持：新增短语必须能由相同 tokenizer 表达，还要在目标距离、噪声、口音和误触发
场景中验证。解析器允许 32 条不代表模型在 32 条时仍满足资源和效果要求。

提交给管理员前，至少检查 UTF-8、Tab 字段数、重复 ID 和 generation：

```bash
python3 - "$candidate" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
lines = text.splitlines()
assert lines and len(lines[0].split("\t")) == 3
assert lines[0].split("\t")[0] == "xraudio-stage1-keywords-v1"
rows = [line.split("\t") for line in lines[1:]]
assert 1 <= len(rows) <= 32
assert all(len(row) == 6 for row in rows)
ids = [row[0] for row in rows]
assert len(ids) == len(set(ids))
assert any(row[5] == "true" for row in rows)
print(f"结构检查通过：generation={lines[0].split(chr(9))[1]}，词条={len(rows)}")
PY
```

这个检查只验证公开文件结构，不验证模型 token、阈值、识别率，也不替代 Runtime 的
最终校验。

## 4. 原子安装和启用

以下操作仅适用于已经安装 Stage 1 DEV（或未来正式 wake provider）的系统。先把
候选文件安装为同一目录下的 `.new`，再原子替换：

```bash
sudo install -d -m 0750 -o root -g xraudio /etc/xraudio
sudo install -m 0640 -o root -g xraudio \
  "$candidate" /etc/xraudio/stage1-keywords.tsv.new
sudo mv -f /etc/xraudio/stage1-keywords.tsv.new \
  /etc/xraudio/stage1-keywords.tsv
```

不要在运行中的目标文件上逐字节保存。候选配置校验失败时，Runtime 应继续保留上一
代已接受配置。

若离线 Release 明确当前安装的是 Stage 1 DEV profile，重启精确 unit：

```bash
sudo systemctl restart xraudio-stage1-dev.service
sudo systemctl status xraudio-stage1-dev.service --no-pager
```

这个命令不会安装 backend/model。如果系统没有该 unit，或安装的是其他 profile，
应回到对应 Release 文档确认服务名；不要用通配、模糊匹配或批量重启猜测 unit。

## 5. 验证生效结果

先确认 Stage 1 服务启动且日志没有配置拒绝，再启动 wake 订阅并说出已启用词条：

```bash
source /opt/ros/jazzy/setup.bash

sudo journalctl -u xraudio-stage1-dev.service -b -n 100 --no-pager
ros2 topic echo --once /xraudio/status \
  xraudio_ros2_bridge/msg/RuntimeStatus
ros2 topic echo /xraudio/wake \
  xraudio_ros2_bridge/msg/WakeEvent
```

验收时注意：

- 未通过校验时 Runtime 应保留上一代配置，不能半加载；
- `config_id`/`config_generation` 位于新产生的 `WakeEvent` 中，应对应刚安装的配置；
- `keyword_confidence_valid=false` 时置信度数值不是概率；
- 方向是否可用由独立的 direction/sync 字段决定，不能只看关键词是否命中；
- 修改配置后应同时复测目标词命中、非目标语音误触发、环境噪声和所需距离；
- 本 GitHub 仓库的监视器只订阅结果，不负责加载配置或模型。
