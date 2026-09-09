#!/usr/bin/env python3
# Copyright 2026 Shenzhen XiaoR Geek Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Fail on obvious private artifacts and validate the public source skeleton."""

from pathlib import Path
import hashlib
import py_compile
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".md",
    ".py",
    ".sh",
    ".tsv",
    ".xml",
    ".yaml",
    ".yml",
}
FORBIDDEN_BINARY_SUFFIXES = {".bin", ".deb", ".key", ".onnx", ".wav"}
SENSITIVE_PATTERNS = {
    "private IPv4 address": re.compile(
        r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|"
        r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
    ),
    "macOS developer path": re.compile(r"/Users/[^/\s]+/"),
    "development Pi path": re.compile(r"/home/xrrobot/"),
    "real XR serial": re.compile(r"\bXR[0-9A-F]{12}\b"),
    "GitHub token": re.compile(r"\bgh[opsu]_[A-Za-z0-9_]{20,}\b"),
    "private key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
}
APACHE_2_LICENSE_SHA256 = (
    "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
)


def tracked_candidates():
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path == SELF:
            continue
        yield path


def verify_no_private_material(errors):
    for path in tracked_candidates():
        if path.suffix.lower() in FORBIDDEN_BINARY_SUFFIXES:
            errors.append(f"forbidden binary/model artifact: {path.relative_to(ROOT)}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label}: {path.relative_to(ROOT)}")


def verify_package(errors):
    package_root = ROOT / "xraudio_examples"
    manifest = package_root / "package.xml"
    tree = ET.parse(manifest)
    dependencies = {node.text for node in tree.findall(".//exec_depend")}
    if "xraudio_ros2_bridge" not in dependencies:
        errors.append("xraudio_examples must consume the installed bridge message package")
    if list(ROOT.rglob("*.msg")):
        errors.append("public repository must not duplicate bridge message definitions")

    for source in package_root.rglob("*.py"):
        py_compile.compile(str(source), doraise=True)


def verify_keyword_example(errors):
    path = ROOT / "config/keywords.tsv.example"
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].split("\t", 1)[0] != "xraudio-stage1-keywords-v1":
        errors.append("keyword example has an invalid header")
        return
    if len(lines[0].split("\t")) != 3:
        errors.append("keyword example header must have three tab-separated fields")
    for number, line in enumerate(lines[1:], start=2):
        if len(line.split("\t")) != 6:
            errors.append(f"keyword example line {number} must have six fields")


def verify_license(errors):
    license_bytes = (ROOT / "LICENSE").read_bytes()
    if hashlib.sha256(license_bytes).hexdigest() != APACHE_2_LICENSE_SHA256:
        errors.append("LICENSE is not the unmodified Apache License 2.0 text")

    notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
    if "Copyright 2026 Shenzhen XiaoR Geek Technology Co., Ltd." not in notice:
        errors.append("NOTICE is missing the approved copyright holder")
    if "not grant permission" not in notice:
        errors.append("NOTICE is missing the trademark boundary")

    package_xml = (ROOT / "xraudio_examples/package.xml").read_text(encoding="utf-8")
    setup_py = (ROOT / "xraudio_examples/setup.py").read_text(encoding="utf-8")
    if "<license>Apache-2.0</license>" not in package_xml:
        errors.append("package.xml must declare Apache-2.0")
    if 'license="Apache-2.0"' not in setup_py:
        errors.append("setup.py must declare Apache-2.0")


def main():
    errors = []
    verify_no_private_material(errors)
    verify_package(errors)
    verify_keyword_example(errors)
    verify_license(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("public tree verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
