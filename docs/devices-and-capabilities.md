# 设备与能力

## 产品形态

### XR-AUD-01：Standard Audio

- 标准 USB Clean Voice 麦克风；
- 标准两路 Speaker；
- 不要求 Raw Array、DOA、唤醒方向或高级 Runtime。

### XR-AUD-02：Fusion

- 包含 Standard Audio；
- 高级 Runtime 可以独占 Raw-8，并派生 production-6 DOA；
- 可在唤醒词命中后发布结构化方向事件；
- ROS 2 Bridge 只转发 Runtime 已经产生的事件。

“XR-AUD-02”不能代替能力协商。固件、软件包或授权状态变化时，同一型号也可能只
暴露能力子集。

## Capability 规则

应用应读取 `/xraudio/wake` 的 `capabilities`，并结合 `/xraudio/status` 的 Runtime、
SDK、同步和授权状态判断功能。有效的唤醒方向至少需要：

```text
standard-audio
raw-array-8
production-array-6
array-sync-binding
doa
wake-direction
```

只有 `standard-audio` 时，唤醒事件可以存在，但方向应为 `unsupported`。Fusion
设备没有得到有效测量时，方向是 `unavailable`。应用不能把这两种情况的数值零当作
0 度测量。

## 多设备部署

每个 Runtime/Bridge 实例必须绑定完整 exact serial，并使用独立 namespace，例如：

```text
/xraudio/front/status
/xraudio/front/wake
/xraudio/rear/status
/xraudio/rear/wake
```

不得使用 ALSA 卡号、动态 PipeWire ID、USB 插入顺序或产品名称代替设备身份。
示例监视器的 `expected_serial` 仅用于对带 serial 的消息做额外核对；真正的设备绑定
必须在 Runtime/Bridge 层完成。

## 数据所有权

- Runtime 是 Raw-8 的唯一 owner；
- Bridge 只读取 system D-Bus；
- 本仓库示例只订阅 ROS 2 topic；
- ROS 应用不得再次打开 Raw Array，也不得自行复制底层 DOA/KWS；
- Standard Speaker/Clean Voice 始终保持系统音频用途。
