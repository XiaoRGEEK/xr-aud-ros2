# XR-AUD ROS 2

本仓库是 XR-AUD 系列设备面向用户的 ROS 2 接入入口，提供配置示例、启动文件、
订阅示例和部署文档。

它**不是 Linux 音频驱动**。XR-AUD 的 Standard Audio 使用 Linux 原生支持的
USB Audio Class：Clean Voice 是普通麦克风输入，两路 Speaker 是普通音频输出。
只有状态、声源方向（DOA）、唤醒词方向等高级能力，才需要额外安装二进制
XR Audio Runtime 和 `xraudio-ros2-bridge`。

[English](README.md)

## 产品区分

| 产品 | 形态 | 对外能力 |
| --- | --- | --- |
| XR-AUD-01 | Standard Audio | 标准 USB Clean Voice 麦克风和两路 Speaker；不依赖高级 Runtime。 |
| XR-AUD-02 | Fusion | 在 Standard Audio 之外，通过已安装 Runtime 提供受 capability 约束的 Raw Array 和 DOA；唤醒事件还要求当前仅限 DEV 的 Stage 1 profile，以及单独提供的 backend/model。 |

应用必须读取设备和 Runtime 明确声明的 capability，不能根据产品名、USB 通道数、
ALSA 卡号或“是否看见某个 topic”猜测功能。这样未来 XR-AUD-03、XR-AUD-04
增加或裁剪硬件时，应用接口仍能保持一致。

## 仓库内容

- `xraudio_examples`：可由 ROS 2 Jazzy `colcon` 构建的 Python 示例包；
- `/xraudio/status`、`/xraudio/doa`、`/xraudio/wake` 的只读订阅示例；
- 单设备 launch 和参数配置示例；
- 唤醒词 TSV 配置模板；
- 安装、能力、ROS 2 API 和故障排查文档；
- 防止密钥、内网地址和开发环境信息误入公开仓库的检查脚本。

ROS 消息由已安装的 `xraudio_ros2_bridge` 包提供。本仓库不复制消息定义，避免
形成两个逐渐不一致的公开接口。

## 快速开始

基础 Clean Voice 和 Speaker 不需要安装本仓库中的“驱动”。高级 ROS 2 功能需要
管理员先配置软件源并安装 Runtime/Bridge：

```bash
sudo apt install xraudio-runtime xraudio-ros2-bridge

source /opt/ros/jazzy/setup.bash
mkdir -p ~/xr_aud_ws/src
git clone https://github.com/XiaoRGEEK/xr-aud-ros2.git \
  ~/xr_aud_ws/src/xr-aud-ros2
cd ~/xr_aud_ws
colcon build --packages-select xraudio_examples
source install/setup.bash

ros2 launch xraudio_examples monitor.launch.py \
  topic_prefix:=/xraudio expected_serial:=请填写完整设备序列号
```

示例程序只是订阅者：它不会打开 USB/Raw-8，不会成为第二个采集 owner，不会修改
默认麦克风和喇叭，也不包含 DOA/KWS 算法。

二进制 provider 安装并正确配置后，公开示例可以直接消费 status 和 DOA。上面的
命令不会安装或启用 KWS backend/model，因此仅按这份 README 操作不会产生 wake
事件。

详细内容见：

- [安装说明](docs/installation.md)
- [设备与能力](docs/devices-and-capabilities.md)
- [唤醒词配置](docs/wake-word-configuration.md)
- [ROS 2 API](docs/ros2-api.md)
- [故障排查](docs/troubleshooting.md)
- [CI 与测试边界](docs/ci-and-testing.md)

## 当前公开边界

唤醒词配置格式和消息契约可以公开，但当前 Stage 1 producer 仍是 DEV 部署；用于
验证的 KWS 模型权重许可尚未完成书面确认，因此不能进入本仓库、DEB、镜像或公开
下载。普通公开用户不能只依靠本 README 获得 wake 事件。只有安装了许可明确、与
Runtime 兼容的 backend/model 包后，才能把唤醒事件作为公开产品能力交付。

完整边界见 [PUBLIC_RELEASE_BOUNDARY.md](PUBLIC_RELEASE_BOUNDARY.md)。本仓库暂未
选择正式开源许可证；复制或再分发前请阅读 [LICENSE_DECISION.md](LICENSE_DECISION.md)。
