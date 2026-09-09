from glob import glob
from setuptools import find_packages, setup


PACKAGE_NAME = "xraudio_examples"


setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + PACKAGE_NAME]),
        ("share/" + PACKAGE_NAME, ["package.xml"]),
        ("share/" + PACKAGE_NAME + "/launch", glob("launch/*.launch.py")),
        ("share/" + PACKAGE_NAME + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="XR-AUD maintainers",
    maintainer_email="maintainers@example.invalid",
    description="Read-only ROS 2 examples for the installed XR Audio bridge.",
    license="To be determined; see LICENSE_DECISION.md",
    url="https://github.com/XiaoRGEEK/xr-aud-ros2",
    entry_points={
        "console_scripts": [
            "event_monitor = xraudio_examples.event_monitor:main",
        ],
    },
)
