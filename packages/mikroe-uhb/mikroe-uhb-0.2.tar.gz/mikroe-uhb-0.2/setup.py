#!/usr/bin/python
from setuptools import setup, find_packages
import sys

install_requires = []
if sys.platform.startswith("linux"):
    install_requires += ["pyudev>=0.13"]
else:
    install_requires += ["hidapi>=0.7.99"]

setup(
    name = "mikroe-uhb",
    version = "0.2",
    packages = find_packages(exclude=["*.tests"]),
    description = "USB HID Bootloader programmer for MikroElektronika devices",
    url = "https://github.com/thotypous/mikroe-uhb",
    download_url = "https://github.com/thotypous/mikroe-uhb/archive/v0.2.tar.gz",
    keywords = ["microcontroller", "usb", "programmer"],
    install_requires = install_requires,
    test_suite = "mikroeuhb.tests",
    scripts = ["mikroe-uhb"],
    use_2to3 = True,
)
