# XR-AUD ROS 2

Public ROS 2 integration, configuration examples, and deployment guidance for
the XR-AUD product family.

This repository is **not a Linux audio driver or the ROS event provider**.
XR-AUD Standard Audio uses the USB Audio Class supported by Linux: Clean Voice
is a normal microphone source and the stereo speaker is a normal audio sink.
Separately supplied XR Audio Runtime and `xraudio-ros2-bridge` binary packages
own the advanced processing and publish read-only ROS 2 events such as status,
direction of arrival (DOA), and wake phrase direction. This repository contains
subscriber examples for those events.

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

The currently verified advanced baseline is **Raspberry Pi 5, Ubuntu 24.04
ARM64, and ROS 2 Jazzy**. Standard USB Audio may enumerate on more class-
compliant Linux systems, but that does not imply that the advanced Runtime,
DOA, wake, or ROS 2 stack has been qualified there.

The online APT/DEB channel is still in deployment testing and is not a stable
public installation route. Authorized internal/evaluation users should contact
XRGEEK through their existing product or support channel for the offline
**XR-AUD-02 DEV v0.2.0** ZIP and its release-specific instructions. The bundle
provides the proprietary SDK, Runtime, ROS provider, and separately governed
backend/model assets; none of them is stored in this public repository.

After installing and enabling that provider exactly as described by the
offline release, verify the provider before building this repository:

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic list -t | grep '^/xraudio/'
ros2 topic echo --once /xraudio/status \
  xraudio_ros2_bridge/msg/RuntimeStatus
```

The commands above test the provider installed by the offline DEB bundle; they
do not run code from this GitHub repository. Once `/xraudio/status`,
`/xraudio/doa`, and (for a configured Stage 1 profile) `/xraudio/wake` are
available, build and run the public subscriber example:

```bash
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
It also does **not** install or enable a KWS backend/model. Wake events require
an installed Stage 1 provider, model assets supplied under their own terms,
and a validated keyword configuration.

See [Installation](docs/installation.md),
[devices and capabilities](docs/devices-and-capabilities.md),
[wake phrase configuration](docs/wake-word-configuration.md),
[ROS 2 API](docs/ros2-api.md), and
[troubleshooting](docs/troubleshooting.md).

CI scope and its explicit dependency-aware skip are documented in
[CI and testing](docs/ci-and-testing.md).

## Current boundary

The public configuration format and wake message contract are available, but
the current Stage 1 wake producer remains a controlled DEV deployment. Model
assets are not distributed in this repository, a public Debian repository, or
an image. Following only this README cannot create wake events. A compatible,
authorized backend/model package is required. The offline DEV bundle is for
authorized evaluation and is not a declaration of public production support.
See [PUBLIC_RELEASE_BOUNDARY.md](PUBLIC_RELEASE_BOUNDARY.md).

The source and documentation in this repository are available under the
[Apache License 2.0](LICENSE), including commercial use subject to its terms.
See [NOTICE](NOTICE) for attribution and trademark information. The license
does not cover separately distributed private Runtime, SDK, firmware, model,
or production-tool components.
