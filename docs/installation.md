# 安装与验证

## 1. 先区分两层能力

### Standard Audio

XR-AUD-01 和 XR-AUD-02 的 Standard Audio 使用标准 USB Audio Class。连接设备后，
Linux 应当直接枚举 Clean Voice 输入和两路 Speaker 输出，不需要本仓库提供专用
内核驱动。

如果系统需要在开机或热插拔后自动选择 XR-AUD 的 Clean Voice/Speaker，可使用
厂商提供的 `xraudio-audio-defaults` 包。它只负责系统音频默认策略，不包含
Raw-8、DOA、唤醒、Runtime 或 ROS 2。

### 高级 Runtime 与 ROS 2

当前高级功能经过验证的主机基线是：

- Raspberry Pi 5；
- Ubuntu 24.04 ARM64；
- ROS 2 Jazzy。

标准 UAC 在其他 Linux 系统上可以工作，不等于高级 Runtime/DOA/唤醒/ROS 2 已在
该系统完成验证。公开示例也不是 provider：真正的设备绑定、Raw-8 单一 owner、
DOA/KWS 和 ROS 消息发布由另行安装的私有软件包负责。

## 2. 取得并安装 provider

在线 APT/DEB 仓仍处于部署测试，当前不是稳定的公众安装入口。请勿把下面的离线
流程改写成面向公众可用的 `sudo apt install xraudio-...` 承诺。

已授权的内部/评估用户请通过既有产品或支持渠道联系 XRGEEK，获取离线
**XR-AUD-02 DEV v0.2.0** ZIP、完整性校验值及该版本的安装说明。离线 Release
会提供匹配版本的私有 SDK、Runtime、ROS provider，以及受单独条款约束的
backend/model。GitHub 本仓库不包含这些组件，也不提供离线包下载地址。

严格按离线包内的说明执行校验、安装、exact serial 配置、授权和服务启用。若版本
说明要求手工安装 DEB，应让 APT 在同一条命令中解析该 Release BOM 的所有包，例如：

```bash
sudo apt install ./libxraudio0_*.deb \
  ./xraudio-runtime_*.deb \
  ./xraudio-ros2-bridge_*.deb
```

这只是离线安装模式示例，文件清单和 Stage 1 安装入口以当前 Release 为准。不要用
`dpkg -i` 忽略依赖，不要混合不同 Release 的 DEB，也不要从开发构建目录复制临时
`.so` 到系统路径。

Bridge 只读取 Runtime system D-Bus，不应猜测设备序列号或自行打开 USB。请按离线
Release 模板填写完整 exact serial 并显式启用对应服务。多设备部署时，每台设备
必须绑定不同 serial，并使用独立 ROS namespace。

## 3. 先验证离线 DEB provider

安装并启用 provider 后，先不要克隆 GitHub 示例。用 ROS 2 自带命令确认安装包已经
提供消息类型、节点和话题：

```bash
source /opt/ros/jazzy/setup.bash

ros2 pkg prefix xraudio_ros2_bridge
ros2 topic list -t | grep '^/xraudio/'
ros2 topic echo --once /xraudio/status \
  xraudio_ros2_bridge/msg/RuntimeStatus
```

上述 `ros2 topic echo` 测试的是离线 DEB 安装的 provider，和本 GitHub 仓库中的
示例节点无关。当前接口应包括：

```text
/xraudio/status  xraudio_ros2_bridge/msg/RuntimeStatus
/xraudio/doa     xraudio_ros2_bridge/msg/Doa
/xraudio/wake    xraudio_ros2_bridge/msg/WakeEvent
```

`/xraudio/wake` 是瞬时事件流。只有已安装并启用兼容 Stage 1 profile、模型和有效
唤醒词配置时，说出已配置词条才会产生事件。可以在说唤醒词前启动：

```bash
ros2 topic echo /xraudio/wake \
  xraudio_ros2_bridge/msg/WakeEvent
```

如果 Standard Audio 可以播放/录音，但 `ros2 pkg prefix` 或 status 检查失败，应先
修复 provider 安装与服务状态；编译公开示例不会补齐私有 provider。

## 4. 下载并构建公开订阅示例

provider 自检通过后，再执行：

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

`xraudio_examples` 编译时依赖已安装 Bridge 所拥有的消息包。若构建提示找不到
`xraudio_ros2_bridge`，应回到第 3 步修复匹配版本的 Bridge；不能复制一份 `.msg`
绕过依赖。

## 5. 运行公开监视器

```bash
source /opt/ros/jazzy/setup.bash
source ~/xr_aud_ws/install/setup.bash

ros2 launch xraudio_examples monitor.launch.py \
  topic_prefix:=/xraudio \
  expected_serial:=YOUR_EXACT_DEVICE_SERIAL
```

也可以直接运行：

```bash
ros2 run xraudio_examples event_monitor --ros-args \
  -p topic_prefix:=/xraudio \
  -p expected_serial:=YOUR_EXACT_DEVICE_SERIAL
```

这个监视器只是只读 subscriber。它不会启动/停止 Runtime，不会打开 USB、Raw-8、
ALSA 或 PipeWire，不会修改默认音频设备，也不会实现 DOA/KWS。删除 workspace 只会
删除公开示例，不会卸载 provider 或影响 Standard Audio。

## 6. 唤醒词和卸载边界

需要修改唤醒词时，继续阅读[唤醒词配置](wake-word-configuration.md)。只有系统已经
安装对应 Stage 1 profile/backend/model 时，TSV 才会生效；创建配置文件本身不会
安装 KWS。

卸载私有 provider、Runtime 或音频默认策略时，请遵守离线 Release 的回退说明。
不要根据本公开仓库猜测包名、服务依赖或删除顺序。
