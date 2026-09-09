"""Test that the example preserves bridge validity semantics."""

from types import SimpleNamespace
import unittest

from xraudio_examples.event_format import format_event


class FakeMessage(SimpleNamespace):
    """Small duck-typed substitute for generated ROS messages."""

    def get_fields_and_field_types(self):
        return {name: "fixture" for name in vars(self)}


class EventFormatTest(unittest.TestCase):
    """Exercise the public formatter without ROS or hardware."""

    def test_wake_keeps_measured_but_unusable_angle(self):
        message = FakeMessage(
            direction_measurement_available=True,
            direction_usable=False,
            direction_availability="measured",
            angle_deg=42.5,
            heuristic_quality=0.2,
        )
        record = format_event("wake", message)
        self.assertEqual(record["direction_decision"], "measured_not_usable")
        self.assertEqual(record["message"]["angle_deg"], 42.5)

    def test_wake_does_not_invent_measurement(self):
        message = FakeMessage(
            direction_measurement_available=False,
            direction_usable=False,
            direction_availability="unsupported",
            angle_deg=0.0,
        )
        record = format_event("wake", message)
        self.assertEqual(record["direction_decision"], "unsupported")

    def test_doa_respects_valid_flag(self):
        message = FakeMessage(valid=False, azimuth_degrees=270.0, reason="sync_lost")
        record = format_event("doa", message)
        self.assertEqual(record["direction_decision"], "invalid")
        self.assertEqual(record["message"]["reason"], "sync_lost")


if __name__ == "__main__":
    unittest.main()
