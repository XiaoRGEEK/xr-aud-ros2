# XR-AUD ROS 2

Public ROS 2 integration, configuration examples, and deployment guidance for
the XR-AUD product family.

This repository is **not a Linux audio driver**. XR-AUD Standard Audio uses the
USB Audio Class supported by Linux: Clean Voice is a normal microphone source
and the stereo speaker is a normal audio sink. The optional XR Audio Runtime
and `xraudio-ros2-bridge` binary packages provide advanced, read-only ROS 2
events such as status, direction of arrival (DOA), and wake phrase direction.

[中文说明](README.zh-CN.md)

## Product profiles

| Product | Profile | Public host behavior |
| --- | --- | --- |
| XR-AUD-01 | Standard Audio | Clean Voice microphone and stereo speaker through standard USB Audio; no advanced Runtime is required. |
| XR-AUD-02 | Fusion | Standard Audio plus capability-gated Raw Array processing and DOA from an installed Runtime. Wake events additionally require the current DEV-only Stage 1 profile and separately supplied backend/model assets. |

Applications must use advertised capabilities. They must not infer support
from the product name, USB channel count, ALSA card number, or topic presence.
This rule allows future XR-AUD hardware to add or remove features without
breaking applications.

## What is in this repository

- `xraudio_examples`: a buildable ROS 2 Jazzy Python package that subscribes
  to the installed bridge's `/xraudio/status`, `/xraudio/doa`, and
  `/xraudio/wake` topics without opening the device;
- launch and parameter examples for a single device;
- a bounded wake phrase TSV configuration example;
- installation, capability, API, and troubleshooting documentation;
- public-tree checks that reject common secret and private-environment leaks.

The ROS messages are owned by the installed `xraudio_ros2_bridge` package.
This repository deliberately depends on that package instead of copying its
message definitions and allowing the two contracts to drift.

## Quick start

Prerequisites:

- Ubuntu 24.04 or a compatible ARM64 Linux distribution;
- ROS 2 Jazzy;
- an XR-AUD device and, for advanced features, vendor-provided Runtime and
  bridge packages installed from an operator-configured package source.

Standard Audio needs no repository-specific driver. For advanced ROS 2 use:

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
  topic_prefix:=/xraudio expected_serial:=YOUR_EXACT_DEVICE_SERIAL
```

The example is a subscriber only. It does not start the proprietary Runtime,
open Raw-8, change the default microphone/speaker, or implement DOA/KWS.
After the binary provider is installed and configured, the public example can
consume status and DOA. The command above does **not** install or enable a KWS
backend/model and therefore does not, by itself, produce wake events.

See [Installation](docs/installation.md),
[devices and capabilities](docs/devices-and-capabilities.md),
[wake phrase configuration](docs/wake-word-configuration.md),
[ROS 2 API](docs/ros2-api.md), and
[troubleshooting](docs/troubleshooting.md).

CI scope and its explicit dependency-aware skip are documented in
[CI and testing](docs/ci-and-testing.md).

## Current boundary

The public configuration format and wake message contract are available, but
the current Stage 1 wake producer remains a DEV deployment. Its evaluation-only
KWS model weights are not distributed here, in a Debian package, or in an
image. Ordinary public users cannot obtain wake events by following only this
README. A compatible legally distributable backend/model package is required
before wake events can be presented as a public production feature. See
[PUBLIC_RELEASE_BOUNDARY.md](PUBLIC_RELEASE_BOUNDARY.md).

The source and documentation in this repository are available under the
[Apache License 2.0](LICENSE), including commercial use subject to its terms.
See [NOTICE](NOTICE) for attribution and trademark information. The license
does not cover separately distributed private Runtime, SDK, firmware, model,
or production-tool components.
