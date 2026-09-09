# ROS 2 API

接口由二进制包 `xraudio_ros2_bridge` 1.3.0 提供。默认 namespace 是 `/xraudio`。

| Topic | 类型 | QoS | 用途 |
| --- | --- | --- | --- |
| `/xraudio/status` | `xraudio_ros2_bridge/msg/RuntimeStatus` | reliable, transient-local, depth 1 | Runtime、设备、SDK、同步、授权和丢失状态 |
| `/xraudio/doa` | `xraudio_ros2_bridge/msg/Doa` | best-effort, volatile, depth 8 | 连续 DOA 诊断流 |
| `/xraudio/wake` | `xraudio_ros2_bridge/msg/WakeEvent` | reliable, volatile, depth 16 | 唤醒词命中及其关联方向 |

本仓库不重新定义这些消息。安装的消息包是唯一编译契约；消息 hash 变化后，订阅者
必须重新构建。

## WakeEvent 使用规则

推荐应用首先检查：

1. `keyword_id` 与 `config_generation`；
2. `timing_valid`；
3. `direction_availability`；
4. `direction_measurement_available`；
5. `direction_usable` 和 `sync_admissible`；
6. `angle_deg`、`heuristic_quality`、观察数和 `background_competition`；
7. `direction_reason` 及所有丢失计数。

`heuristic_quality` 不是概率。低质量测量仍可以保留角度，由应用决定是否采用。
只有 `direction_measurement_available=true` 时 `angle_deg` 才表示真实测量；否则 ROS
数值类型中的零只是占位值。

同理，只有 `keyword_confidence_valid=true` 时 `keyword_confidence_value` 才有意义。
当前 backend 可能明确发布 `confidence_kind=unavailable`。

## Doa 使用规则

`Doa.valid=false` 时仍应记录 `reason`、generation、sequence、同步状态和 counters，
但不能把 `azimuth_degrees` 作为产品方向。该 topic 是诊断/连续流，不等价于“某次
唤醒词的方向”；产品应用优先消费 `/xraudio/wake`。

## 时间与重连

ROS `stamp` 是 Bridge 根据 Runtime monotonic 时间映射的 ROS 时间。跨事件排序和
关联仍应保留原始 `*_monotonic_ns`、generation 和 sequence。

Runtime 重启、USB 重连、generation 变化、同步失效、计数增加或序列跳变时，Bridge
会拒绝复用旧证据。应用不应缓存上一角度填补当前无测量事件。

## 查看接口

```bash
source /opt/ros/jazzy/setup.bash
ros2 interface show xraudio_ros2_bridge/msg/WakeEvent
ros2 interface show xraudio_ros2_bridge/msg/Doa
ros2 interface show xraudio_ros2_bridge/msg/RuntimeStatus

ros2 topic info --verbose /xraudio/status
ros2 topic info --verbose /xraudio/doa
ros2 topic info --verbose /xraudio/wake
```
