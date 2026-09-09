# 唤醒词配置

## 当前范围

公开接口允许配置多条唤醒短语，但配置词条不等于替换声学模型。配置只有在系统已经
安装兼容且许可明确的 KWS backend/model 时才会生效。

当前内部验证权重属于 evaluation-only 边界，不能进入本仓库、DEB、系统镜像或公开
下载。公开产品支持的词条数量、语言和模型包应以对应 Release 说明为准。

## 文件格式

参考 [`config/keywords.tsv.example`](../config/keywords.tsv.example)。文件必须是
UTF-8 TSV，真正的分隔符是 Tab，而不是空格或字符串 `\t`：

```text
xraudio-stage1-keywords-v1<TAB>generation<TAB>config-id
id<TAB>显示文字<TAB>模型 tokens<TAB>boost<TAB>decoder threshold<TAB>true|false
```

约束：

- 文件最大 64 KiB；
- 单行最大 4096 字节；
- 最多 32 条结构记录，但这只是解析安全上限，不是性能承诺；
- `id` 必须唯一，至少一条记录启用；
- `boost` 留空表示 backend 默认值，否则必须大于 0；
- `decoder threshold` 留空表示 backend 默认值，否则必须在 0..1；
- `generation` 必须比当前配置更大；
- 整份候选文件验证通过后才替换当前配置，部分有效不会部分生效。

## 安装与更新

首次创建配置：

```bash
sudo install -d -m 0750 -o root -g xraudio /etc/xraudio
sudo install -m 0640 -o root -g xraudio \
  config/keywords.tsv.example /etc/xraudio/stage1-keywords.tsv
```

更新时先复制到同目录的临时文件，检查 Tab、编码、唯一 ID 和递增 generation，再由
管理员原子替换。不要直接在运行中的目标文件上逐字节保存。

```bash
sudo install -m 0640 -o root -g xraudio \
  /path/to/validated-keywords.tsv /etc/xraudio/stage1-keywords.tsv.new
sudo mv /etc/xraudio/stage1-keywords.tsv.new \
  /etc/xraudio/stage1-keywords.tsv
```

由对应 Runtime Release 的说明执行配置 reload 或重启。开发版通常使用：

```bash
sudo systemctl restart xraudio-stage1-dev.service
```

服务名是发布契约的一部分；如果系统安装的是其他 profile，请使用该版本文档给出的
unit，不要通过模糊匹配批量重启服务。

## 验证

修改后检查 `/xraudio/status` 和 `/xraudio/wake`：

- `config_id`/`config_generation` 应对应新配置；
- 未通过校验时 Runtime 应保留上一代配置；
- `keyword_confidence_valid=false` 时数值字段不是概率；
- 方向是否可用由独立的 direction/sync 字段决定，不能仅看关键词是否命中。
