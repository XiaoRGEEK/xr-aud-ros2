# XR-AUD ROS 2

本仓库是 XR-AUD 系列设备面向用户的 ROS 2 接入入口，提供配置示例、启动文件、
订阅示例和部署文档。

它**不是 Linux 音频驱动，也不是 ROS 事件 provider**。XR-AUD 的 Standard Audio
使用 Linux 原生支持的 USB Audio Class：Clean Voice 是普通麦克风输入，两路
Speaker 是普通音频输出。另行提供的二进制 XR Audio Runtime 与
`xraudio-ros2-bridge` 负责高级处理并发布状态、声源方向（DOA）、唤醒词方向等
只读 ROS 2 事件；本仓库只提供这些事件的订阅示例。

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

当前高级功能经过验证的基线是 **Raspberry Pi 5 + Ubuntu 24.04 ARM64 + ROS 2
Jazzy**。标准 USB Audio 可能在更多兼容 UAC 的 Linux 系统上直接枚举，但这不代表
高级 Runtime、DOA、唤醒或 ROS 2 链路已经在这些系统上完成适配验证。

在线 APT/DEB 仓仍在部署测试中，暂时不是稳定的公众安装入口。已授权的内部/评估
用户请通过既有产品或支持渠道联系 XRGEEK，获取离线 **XR-AUD-02 DEV v0.2.0**
ZIP 及其版本说明。离线包提供私有 SDK、Runtime、ROS provider，以及受单独条款
约束的 backend/model；这些内容都不在本公开仓库中。

严格按离线 Release 的说明安装并启用 provider 后，先验证 provider：

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic list -t | grep '^/xraudio/'
ros2 topic echo --once /xraudio/status \
  xraudio_ros2_bridge/msg/RuntimeStatus
```

以上命令测试的是离线 DEB 安装的 provider，不是在运行本 GitHub 仓库的节点。
确认 `/xraudio/status`、`/xraudio/doa`，以及已配置 Stage 1 profile 时的
`/xraudio/wake` 正常后，再编译并运行公开订阅示例：

```bash
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

公开示例不会安装或启用 KWS backend/model。wake 事件需要已经安装 Stage 1
provider、按各自条款提供的模型资源，以及通过校验的唤醒词配置。

详细内容见：

- [安装说明](docs/installation.md)
- [设备与能力](docs/devices-and-capabilities.md)
- [唤醒词配置](docs/wake-word-configuration.md)
- [ROS 2 API](docs/ros2-api.md)
- [故障排查](docs/troubleshooting.md)
- [CI 与测试边界](docs/ci-and-testing.md)

## 当前公开边界

唤醒词配置格式和消息契约可以公开，但当前 Stage 1 producer 仍是受控 DEV 部署；
模型资源不会进入本仓库、公开 DEB 仓或系统镜像。普通公开用户不能只依靠本
README 获得 wake 事件；必须另行取得兼容且获授权的 backend/model。离线 DEV 包
只用于已授权评估，不代表已经面向公众承诺生产支持。

完整边界见 [PUBLIC_RELEASE_BOUNDARY.md](PUBLIC_RELEASE_BOUNDARY.md)。本仓库内发布
的源码和文档采用 [Apache License 2.0](LICENSE)，允许在遵守许可证条款的前提下
商用。归属与商标说明见 [NOTICE](NOTICE)；独立分发的私有 Runtime、SDK、固件、
模型和生产工具不因与本仓库互操作而自动进入该许可证范围。
