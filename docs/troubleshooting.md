# 故障排查

## 能播放/录音，但没有 ROS topic

这是合理的分层结果：Standard Audio 是 USB Audio，不依赖 Runtime/ROS。检查高级包
和服务是否安装、启用：

```bash
systemctl status xraudio-ros2-bridge.service --no-pager
ros2 node list
ros2 topic list | grep '^/xraudio/'
```

不要通过改默认声卡或以 root 运行 ROS 节点解决 Bridge 问题。

## 有 status，没有 wake

- wake 是事件流，不保留历史；订阅者必须在命中前启动；
- 确认 Runtime interface 支持 wake schema；
- 确认兼容的 KWS backend/model 已合法安装；
- 检查词条配置、generation 和服务日志；
- 普通语音或环境噪声不应产生 wake 事件。

## wake 有关键词，但方向不可用

读取 `direction_availability`、`direction_measurement_available`、
`direction_usable`、`sync_admissible` 和 `direction_reason`。Standard Audio-only
设备的方向是 `unsupported`；Fusion 暂时没有测量时是 `unavailable`。不能用上一次
角度或连续 DOA 流替代本次唤醒方向。

## 角度存在但 usable=false

这通常表示确实测得了低质量或同步不合格的方向。保留角度和质量元数据供应用策略
使用，但不要把 `heuristic_quality` 当成概率。检查背景竞争、观察数、公共 mask、
Wire 同步和丢失计数。

## 找不到 xraudio_ros2_bridge 消息

```bash
source /opt/ros/jazzy/setup.bash
ros2 pkg prefix xraudio_ros2_bridge
```

如果失败，应从已授权的离线 Release 安装匹配版本的 Bridge DEB。在线 APT/DEB 仓
仍在部署测试，不能假定当前公众环境已经配置该软件源。不要从其他仓库复制 `.msg`
文件，因为这样可能编译出与运行服务不兼容的消息 hash。

## 多设备事件混在一起

每台设备分别配置 exact serial 和 namespace。不要用空 serial、ALSA card index 或
插入顺序做多板绑定。订阅者也可以设置 `expected_serial` 对带 serial 的事件再检查。

## USB 拔插后不恢复

先看 Runtime/Bridge systemd 状态和日志，再核对 status 中的 generation、同步状态和
丢失计数。不要启动第二个采集程序“探测”Raw Array；这会与 Runtime 的唯一 owner
规则冲突。Standard Audio 正常并不自动证明高级 Raw/DOA epoch 已恢复。
