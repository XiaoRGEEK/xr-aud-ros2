# CI 与测试边界

公开 CI 执行：

- Python/XML/TSV 和 shell 语法检查；
- 常见内网地址、真实开发路径、真实序列号、密钥和模型工件扫描；
- 确认示例依赖 `xraudio_ros2_bridge`，且仓库没有复制 `.msg`；
- 当 runner 同时具备 ROS 2 Jazzy 和公开可安装的 Bridge provider 时，运行真实
  `colcon build/test`。

当前 GitHub 托管 runner 没有厂商 Bridge 二进制消息包，因此 colcon 步骤会明确输出
`SKIP`。它不下载私有依赖，不生成假的消息包，也不能作为硬件、Runtime、DOA 或
唤醒词通过的证据。

完整 ROS 验证应在安装了发布版 `xraudio-ros2-bridge` 的 Jazzy 系统上运行：

```bash
source /opt/ros/jazzy/setup.bash
colcon build --packages-select xraudio_examples
source install/setup.bash
colcon test --packages-select xraudio_examples
colcon test-result --verbose
```

后续若 Bridge 的消息/provider 形成公开 APT 分发，可以在 GitHub Actions 中加入该
公开、签名且无需凭据的源，把当前显式 SKIP 升级为强制 colcon 门禁。
