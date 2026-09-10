# XR-AUD ROS 2 示例

这是 XR-AUD 的公开 ROS 2 只读示例仓库。它订阅设备服务已经发布的状态、实时声源
方向（DOA）和唤醒事件，并将消息打印为 JSON；不会打开 USB/Raw-8、实现算法、修改
默认声卡或控制设备。

> 当前高级功能验证环境：Raspberry Pi 5、Ubuntu 24.04 ARM64、ROS 2 Jazzy。
> 在线 DEB 源仍在测试。内部或已授权用户请联系 XRGEEK 获取离线安装 ZIP。

## 1. 安装前提

系统需要提前安装：

- ROS 2 Jazzy；
- `colcon`、`rosdep` 和 Python 3；
- 与设备版本匹配的 XR Audio Runtime 和 `xraudio_ros2_bridge` provider。

Runtime、SDK、模型和授权不在本公开仓库。当前内部 DEV ZIP 自带安装脚本和版本说明，
应以 ZIP 内说明为准，例如：

```bash
sudo bash tools/install-stage1-dev.sh \
  --serial YOUR_EXACT_DEVICE_SERIAL \
  --speech-user "$USER" \
  --enable
```

先确认 provider 已经运行：

```bash
source /opt/ros/jazzy/setup.bash
ros2 pkg prefix xraudio_ros2_bridge
ros2 topic list -t | grep '^/xraudio/'
ros2 topic echo --once /xraudio/status \
  xraudio_ros2_bridge/msg/RuntimeStatus
```

正常情况下可以看到 `/xraudio/status`、`/xraudio/doa` 和 `/xraudio/wake`。
Standard Audio（Clean Voice + Speaker）是标准 USB Audio，不依赖本示例；高级事件才需要
Runtime/provider。

## 2. 下载和编译示例

```bash
source /opt/ros/jazzy/setup.bash
mkdir -p ~/xr_aud_ws/src
git clone https://github.com/XiaoRGEEK/xr-aud-ros2.git \
  ~/xr_aud_ws/src/xr-aud-ros2
cd ~/xr_aud_ws

rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys xraudio_ros2_bridge
colcon build --packages-select xraudio_examples
source install/setup.bash
```

## 3. 运行示例

把参数替换成设备的完整序列号：

```bash
ros2 launch xraudio_examples monitor.launch.py \
  topic_prefix:=/xraudio \
  expected_serial:=YOUR_EXACT_DEVICE_SERIAL
```

终端会输出 `status`、`doa` 和 `wake` JSON。先启动程序，再说出已配置的唤醒词；
`/xraudio/wake` 是实时事件，不会补发历史命中。按 `Ctrl-C` 退出。

常用参数：

| 参数 | 默认值 | 用途 |
| --- | --- | --- |
| `topic_prefix` | `/xraudio` | provider 发布事件的 namespace |
| `expected_serial` | 空 | 对消息中的完整设备序列号做额外核对 |
| `print_status` | `true` | 输出状态事件 |
| `print_doa` | `true` | 输出连续 DOA |
| `print_wake` | `true` | 输出唤醒事件 |

也可以直接查看某个 topic：

```bash
ros2 topic echo /xraudio/wake xraudio_ros2_bridge/msg/WakeEvent
```

## 4. 唤醒词配置边界

[`config/keywords.tsv.example`](config/keywords.tsv.example) 只展示公开配置格式。修改显示
文字并不会自动训练或更换模型；模型 tokens、阈值和支持词条必须与已安装 provider/model
匹配。安装配置、更新 generation 和重启服务应遵循对应离线 Release 的说明。

本示例只读取结果，不写系统配置。当前解析格式最多接受 32 条记录，但这不是识别效果、
CPU 占用或延迟承诺，实际词条数需要在目标环境验收。

## 5. 最小排障

- `xraudio_ros2_bridge` 找不到：provider 尚未安装，或没有 `source` ROS 环境。
- 有 USB 麦克风/喇叭但没有 topic：Standard Audio 正常，不代表高级 Runtime 已运行。
- 有 `status` 但没有 `wake`：先启动订阅，再检查 Stage 1、模型、授权和词条配置。
- 有角度但不可用：保留测量值，同时检查 `direction_usable`、同步状态和原因字段。
- USB 重连后异常：检查 Runtime/provider 服务；不要启动第二个程序抢占 Raw-8。
- 多设备：每个 provider 绑定完整 serial，并使用不同 namespace；不要依赖 ALSA 卡号。

消息类型、字段使用规则、QoS 和多设备约定见
[`docs/ROS2接口.md`](docs/ROS2接口.md)。

## 许可与边界

本仓库源码和文档采用 [Apache License 2.0](LICENSE)，归属与商标信息见
[NOTICE](NOTICE)。该许可不覆盖另行分发的 Runtime、SDK、固件、模型、授权或生产工具。
本仓不包含内网地址、私有二进制、模型、密钥、真实设备序列号或私有实现协议。
