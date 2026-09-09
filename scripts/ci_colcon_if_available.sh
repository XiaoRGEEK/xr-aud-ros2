#!/bin/bash
# Copyright 2026 Shenzhen XiaoR Geek Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

if [[ ! -r /opt/ros/jazzy/setup.bash ]]; then
    echo "SKIP: ROS 2 Jazzy is not installed on this runner."
    exit 0
fi

set +u
source /opt/ros/jazzy/setup.bash
set -u

if ! ros2 pkg prefix xraudio_ros2_bridge >/dev/null 2>&1; then
    echo "SKIP: the public xraudio_ros2_bridge provider package is unavailable."
    echo "The repository does not copy private message definitions to fake this dependency."
    exit 0
fi

workspace=$(mktemp -d)
trap 'rm -rf "$workspace"' EXIT
mkdir -p "$workspace/src"
ln -s "$(pwd)/xraudio_examples" "$workspace/src/xraudio_examples"
cd "$workspace"
colcon build --packages-select xraudio_examples
set +u
source install/setup.bash
set -u
colcon test --packages-select xraudio_examples
colcon test-result --verbose
