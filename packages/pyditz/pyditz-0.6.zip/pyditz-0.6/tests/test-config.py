"""
Configuration tests.
"""

import os
from ditz.config import config


def test_config():
    "Test configuration files"

    config.write_file("test-config.ini")


if __name__ == "__main__":
    test_config()
