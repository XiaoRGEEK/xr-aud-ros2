# ROS 2 接口

## 数据链路

```text
XR-AUD 设备 → XR Audio Runtime → system D-Bus → xraudio_ros2_bridge → ROS 2 应用
```

`xraudio_ros2_bridge` 是消息定义和 provider。本仓库中的 `xraudio_examples` 只是
subscriber，不复制 `.msg`，也不访问底层音频或设备。完整字段以目标系统安装的消息
包为准：

```bash
source /opt/ros/jazzy/setup.bash
ros2 interface show xraudio_ros2_bridge/msg/RuntimeStatus
ros2 interface show xraudio_ros2_bridge/msg/Doa
ros2 interface show xraudio_ros2_bridge/msg/WakeEvent
```

## Topic

默认 namespace 为 `/xraudio`：

| Topic | 消息类型 | QoS | 用途 |
| --- | --- | --- | --- |
| `/xraudio/status` | `xraudio_ros2_bridge/msg/RuntimeStatus` | reliable、transient-local、depth 1 | Runtime、设备、同步和授权状态 |
| `/xraudio/doa` | `xraudio_ros2_bridge/msg/Doa` | best-effort、volatile、depth 8 | 连续 DOA 诊断流 |
| `/xraudio/wake` | `xraudio_ros2_bridge/msg/WakeEvent` | reliable、volatile、depth 16 | 唤醒词及其语音段方向 |

`status` 会保留最近状态；`doa` 和 `wake` 不补发历史消息。

## RuntimeStatus

重点字段分为四组：

- 身份：`device_serial`、`device_product`、USB VID/PID；
- 版本与就绪：`service_state`、`service_enabled`、`sdk_version`、`sdk_ready`；
- 同步与连续性：`capture_generation`、`sync_*`、drop/discontinuity/xrun/sequence 计数；
- 授权与拒绝：`authorized`、`authorization_*`、`rejection_reason`。

应用应先确认完整 serial、服务就绪、授权和同步状态，再使用高级事件。generation 变化或
计数增加表示链路发生过重建或丢失，不能沿用上一代的方向。

## Doa

`Doa` 是连续诊断方向，不等于某次唤醒词的方向：

- 只有 `valid=true` 时才使用 `azimuth_degrees`；
- `reason` 说明无效或降级原因；
- `confidence` 是算法质量指标，不是经过标定的概率；
- `capture_generation`、`sequence`、`sync_*` 和丢失计数用于判断连续性。

需要“谁唤醒、来自哪里”时，优先使用 `/xraudio/wake`，不要把最新一帧连续 DOA
直接拼到唤醒结果上。

## WakeEvent

WakeEvent 是一次自包含的唤醒结果，主要字段包括：

- 关键词：`keyword_id`、`keyword_text`、`config_id`、`config_generation`；
- 关键词置信度：仅当 `keyword_confidence_valid=true` 时数值才有效；
- 时间：`timing_valid`、命中/语音段/关联窗口 monotonic 时间；
- 方向：`direction_availability`、`direction_measurement_available`、
  `direction_usable`、`angle_deg`、`direction_reason`；
- 质量证据：`heuristic_quality`、观察数、`background_competition`、`mask_applied`；
- 链路证据：Clean/Raw generation、`sync_admissible`、同步来源和全部丢失计数。

推荐使用顺序：

1. 核对 `device_serial`、`keyword_id` 和 `config_generation`；
2. 检查 `timing_valid` 和 `direction_measurement_available`；
3. 使用 `direction_usable`、`sync_admissible` 和 `direction_reason` 做业务决策；
4. 当确有测量时保留 `angle_deg` 及其质量证据，即使应用暂不采用。

`heuristic_quality` 不是概率置信度，不能按“0.8 = 80% 准确”解释。当
`direction_measurement_available=false` 时，`angle_deg` 的零值只是消息类型占位，
不代表 0 度测量。

## Exact serial 与多设备

Runtime/provider 必须用完整 exact serial 绑定设备。不得使用 ALSA 卡号、
PipeWire 动态 ID、USB 插入顺序或产品名代替 serial。示例的 `expected_serial` 是
consumer 端的额外核对，不代替 provider 绑定。

多设备应为每个 provider 设置独立 namespace，例如：

```text
/xraudio/front/status
/xraudio/front/doa
/xraudio/front/wake
/xraudio/rear/status
/xraudio/rear/doa
/xraudio/rear/wake
```

消息的 ROS `stamp` 由 Runtime monotonic 时间映射。需要严格排序或关联时，同时保留
monotonic 时间、generation 和 sequence；设备重连后不能用旧角度补当前事件。
