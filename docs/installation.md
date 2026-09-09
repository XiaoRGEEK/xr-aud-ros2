# 安装说明

## 1. Standard Audio

XR-AUD-01 和 XR-AUD-02 的 Standard Audio 使用标准 USB Audio Class。连接设备后，
Linux 应当直接枚举 Clean Voice 输入和两路 Speaker 输出，不需要本仓库提供的专用
内核驱动。

如果系统需要在开机或热插拔后自动选择 XR-AUD 的 Clean Voice/Speaker，可安装
厂商提供的 `xraudio-audio-defaults` 包。它只负责系统音频默认策略，不包含 Raw-8、
DOA、唤醒、Runtime 或 ROS 2。

## 2. 高级 Runtime 与 ROS 2 Bridge（status / DOA）

管理员应先按照发行渠道提供的说明配置 APT 软件源，再安装：

```bash
sudo apt update
sudo apt install xraudio-runtime xraudio-ros2-bridge
```

本公开仓库不硬编码厂商内部或客户私有的软件源地址。若使用离线 DEB，应把同一
Release BOM 中的包放在一个目录，并让 APT 一次解析依赖：

```bash
sudo apt install ./libxraudio0_*.deb \
  ./xraudio-runtime_*.deb \
  ./xraudio-ros2-bridge_*.deb
```

不要用 `dpkg -i` 忽略依赖，也不要从开发构建目录复制临时 `.so` 到系统路径。

Bridge 1.3.0 只读取 Runtime1 system D-Bus。安装包默认不应凭空猜测设备序列号或
自动打开高级服务；请按发行包中的配置模板填写完整 exact serial，并显式启用服务。
多设备部署时，每台设备必须使用不同 ROS namespace。

这一安装集合面向已有二进制 provider 的 status/DOA 接入，不包含 Stage 1 KWS
backend 或模型。`/xraudio/wake` 的类型可以存在，但仅安装上述包不会产生 wake
事件。当前 wake producer 仍属于单独的 DEV profile，普通公开用户不能从本仓库
取得它所需的外部模型资产。

## 3. 构建公开示例

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
colcon test --packages-select xraudio_examples
colcon test-result --verbose
```

`xraudio_examples` 依赖已安装 Bridge 提供的消息包。若 `rosdep` 或构建提示找不到
`xraudio_ros2_bridge`，应先安装匹配的 Bridge 发行包；不能复制一份消息文件临时
绕过依赖。

## 4. 运行只读监视器

```bash
ros2 launch xraudio_examples monitor.launch.py \
  topic_prefix:=/xraudio expected_serial:=YOUR_EXACT_DEVICE_SERIAL
```

也可以直接运行：

```bash
ros2 run xraudio_examples event_monitor --ros-args \
  -p topic_prefix:=/xraudio \
  -p expected_serial:=YOUR_EXACT_DEVICE_SERIAL
```

监视器只订阅事件。它不会启动或停止 Runtime，不会打开设备，也不会更改系统音频。
在普通公开安装中，应先用 status/DOA 验证链路；wake 只有在对应 DEV/未来正式
backend 已明确安装并启用时才可验收。

## 5. 卸载边界

删除本仓库的 workspace 只会删除示例。删除 Bridge 不应删除 Runtime，也不应影响
Standard Audio。生产系统卸载二进制包时，请遵循对应 Release 的回退说明。
