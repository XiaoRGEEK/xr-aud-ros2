# Copyright 2026 Shenzhen XiaoR Geek Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Subscribe to the installed XR Audio bridge without opening audio devices."""

import json

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from xraudio_ros2_bridge.msg import Doa, RuntimeStatus, WakeEvent

from .event_format import format_event


def _topic(prefix, leaf):
    """Join a configured absolute prefix and a fixed topic leaf."""
    normalized = "/" + prefix.strip("/") if prefix.strip("/") else ""
    return normalized + "/" + leaf


class EventMonitor(Node):
    """Log bounded status, DOA, and wake records from one bridge namespace."""

    def __init__(self):
        super().__init__("xraudio_event_monitor")
        self.declare_parameter("topic_prefix", "/xraudio")
        self.declare_parameter("expected_serial", "")
        self.declare_parameter("print_status", True)
        self.declare_parameter("print_doa", True)
        self.declare_parameter("print_wake", True)

        prefix = str(self.get_parameter("topic_prefix").value)
        self.expected_serial = str(self.get_parameter("expected_serial").value)

        status_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        doa_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=8,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        wake_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=16,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )

        if bool(self.get_parameter("print_status").value):
            self.create_subscription(
                RuntimeStatus,
                _topic(prefix, "status"),
                lambda message: self._handle("status", message),
                status_qos,
            )
        if bool(self.get_parameter("print_doa").value):
            self.create_subscription(
                Doa,
                _topic(prefix, "doa"),
                lambda message: self._handle("doa", message),
                doa_qos,
            )
        if bool(self.get_parameter("print_wake").value):
            self.create_subscription(
                WakeEvent,
                _topic(prefix, "wake"),
                lambda message: self._handle("wake", message),
                wake_qos,
            )

        self.get_logger().info(
            "read-only monitor subscribed below %s; expected_serial=%s"
            % (prefix, self.expected_serial or "<bridge-enforced>")
        )

    def _handle(self, kind, message):
        """Reject mismatched serial-bearing events and log all other fields."""
        serial = str(getattr(message, "device_serial", ""))
        if self.expected_serial and serial and serial != self.expected_serial:
            self.get_logger().error(
                "%s event rejected: serial does not match expected_serial" % kind
            )
            return
        record = format_event(kind, message)
        self.get_logger().info(
            json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        )


def main(args=None):
    """Run the read-only monitor until ROS shutdown or Ctrl-C."""
    rclpy.init(args=args)
    node = EventMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
