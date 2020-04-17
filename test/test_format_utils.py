# -*- coding: utf-8 -*-


from collections import namedtuple
from athenacli.packages.format_utils import format_status, humanize_size


def test_format_status_plural():
    assert format_status(rows_length=1) == "1 row in set"
    assert format_status(rows_length=2) == "2 rows in set"

def test_format_status_no_results():
    assert format_status(rows_length=None) == "Query OK"

def test_format_status_with_stats():
    FakeCursor = namedtuple("FakeCursor", ["execution_time_in_millis", "data_scanned_in_bytes"])

    assert format_status(rows_length=1, cursor=FakeCursor(10, 12345678900)) == "1 row in set\nExecution time: 10 ms, Data scanned: 11.5 GB, Approximate cost: $0.06"
    assert format_status(rows_length=2, cursor=FakeCursor(1000, 1234)) == "2 rows in set\nExecution time: 1000 ms, Data scanned: 1.21 KB, Approximate cost: $0.00"

def test_humanize_size():
    assert humanize_size(20) == "20 B"
    assert humanize_size(2000) == "1.95 KB"
    assert humanize_size(200000) == "195.31 KB"
    assert humanize_size(20000000) == "19.07 MB"
    assert humanize_size(200000000000) == "186.26 GB"
