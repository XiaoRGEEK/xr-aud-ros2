# Copyright 2026 Shenzhen XiaoR Geek Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Convert ROS messages to bounded, human-readable JSON records."""

from collections.abc import Mapping, Sequence
import math


MAX_SEQUENCE_ITEMS = 128


def _to_builtin(value):
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Mapping):
        return {str(key): _to_builtin(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_to_builtin(item) for item in value[:MAX_SEQUENCE_ITEMS]]
    if hasattr(value, "get_fields_and_field_types"):
        return {
            field: _to_builtin(getattr(value, field))
            for field in value.get_fields_and_field_types()
        }
    if hasattr(value, "sec") and hasattr(value, "nanosec"):
        return {"sec": int(value.sec), "nanosec": int(value.nanosec)}
    return str(value)


def format_event(topic_kind, message):
    """Return a JSON-serializable event without changing validity semantics."""
    record = {"event": topic_kind, "message": _to_builtin(message)}
    if topic_kind == "wake":
        measured = bool(getattr(message, "direction_measurement_available", False))
        usable = bool(getattr(message, "direction_usable", False))
        if usable:
            decision = "measured_usable"
        elif measured:
            decision = "measured_not_usable"
        else:
            decision = str(getattr(message, "direction_availability", "unknown"))
        record["direction_decision"] = decision
    elif topic_kind == "doa":
        record["direction_decision"] = (
            "measured_usable" if bool(getattr(message, "valid", False)) else "invalid"
        )
    return record
