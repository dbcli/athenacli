# -*- coding: utf-8 -*-


from athenacli.packages.format_utils import format_status


def test_format_status():
    assert format_status(1) == "1 row in set"
    assert format_status(2) == "2 rows in set"
    assert format_status(None) == "Query OK"
