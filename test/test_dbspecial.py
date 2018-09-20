from athenacli.packages.special.utils import format_uptime
from athenacli.packages.completion_engine import (
    suggest_type, Database, View, Schema, Table
)


def test_u_suggests_databases():
    suggestions = suggest_type('\\u ', '\\u ')
    assert suggestions == (Database(),)


def test_describe_table():
    suggestions = suggest_type('\\dt', '\\dt ')
    assert suggestions == (Table(schema=None), View(schema=None), Schema())


def test_list_or_show_create_tables():
    suggestions = suggest_type('\\dt+', '\\dt+ ')
    assert suggestions == (Table(schema=None), View(schema=None), Schema())


def test_format_uptime():
    seconds = 59
    assert '59 sec' == format_uptime(seconds)

    seconds = 120
    assert '2 min 0 sec' == format_uptime(seconds)

    seconds = 54890
    assert '15 hours 14 min 50 sec' == format_uptime(seconds)

    seconds = 598244
    assert '6 days 22 hours 10 min 44 sec' == format_uptime(seconds)

    seconds = 522600
    assert '6 days 1 hour 10 min 0 sec' == format_uptime(seconds)
