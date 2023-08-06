"""
Database export tests.
"""

from ditz.database import DitzDB


def test_html(name="example"):
    "Test exporting HTML"

    db = DitzDB.read(name)
    db.export_html(name + "-html")
