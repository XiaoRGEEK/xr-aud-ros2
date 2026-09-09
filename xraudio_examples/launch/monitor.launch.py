# Copyright 2026 Shenzhen XiaoR Geek Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os


def generate_launch_description():
    package_share = get_package_share_directory("xraudio_examples")
    default_config = os.path.join(package_share, "config", "monitor.yaml")
    return LaunchDescription(
        [
            DeclareLaunchArgument("config", default_value=default_config),
            DeclareLaunchArgument("topic_prefix", default_value="/xraudio"),
            DeclareLaunchArgument("expected_serial", default_value=""),
            Node(
                package="xraudio_examples",
                executable="event_monitor",
                name="xraudio_event_monitor",
                output="screen",
                parameters=[
                    LaunchConfiguration("config"),
                    {
                        "topic_prefix": LaunchConfiguration("topic_prefix"),
                        "expected_serial": LaunchConfiguration("expected_serial"),
                    },
                ],
            ),
        ]
    )
