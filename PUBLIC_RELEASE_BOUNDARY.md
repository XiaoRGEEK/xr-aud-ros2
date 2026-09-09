# Public release boundary

## Included

- ROS 2 Jazzy subscriber examples for the installed
  `xraudio_ros2_bridge` message types;
- launch files and non-secret parameter examples;
- the public wake phrase configuration format;
- user-facing installation and troubleshooting documentation;
- checks that run without hardware or private assets.

## Required binary providers

Advanced functions are provided as separately installed binary packages:

- XR Audio Runtime owns the exact device and the single Raw-8 capture session;
- `xraudio-ros2-bridge` reads Runtime1 system D-Bus and publishes ROS 2 topics;
- the bridge package owns `xraudio_ros2_bridge/msg/WakeEvent`, `Doa`, and
  `RuntimeStatus`.

This repository consumes those interfaces. It does not duplicate their
implementation or message definitions.

## Excluded

- firmware and Recovery source or release images;
- XR Audio SDK and Runtime implementation;
- Raw-8 capture, DOA, AEC, VAD, KWS, ASR, or model-loading algorithms;
- XR Studio and manufacturing tools;
- private model weights, recordings, development licenses, signing material,
  encryption keys, eFuse plans, and provisioning data;
- production VID/PID allocation claims, Secure Boot, Flash Encryption, and
  production authorization policy;
- internal package-server addresses, private repository URLs, machine paths,
  user accounts, and real device serial numbers.

## Ownership and safety

The installed Runtime is the only Raw-8 owner. The ROS bridge and every sample
in this repository are read-only consumers. They must not open USB, ALSA,
PipeWire, HID, or `libxraudio` directly and must not change the system audio
defaults.

Standard Audio remains usable without the Runtime or this repository. Removing
the examples or bridge must not disable the class-compliant Clean Voice source
or stereo speaker sink.

## Model distribution boundary

The keyword configuration interface is public. Evaluation-only model weights
are not. This repository does not imply redistribution permission for any
third-party or internally evaluated model. A later public release must name the
model license, immutable identity, hashes, installation source, and supported
keyword limits before claiming a packaged wake feature.
