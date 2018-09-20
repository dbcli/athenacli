import os
import pytest

from athenacli.packages.completion_engine import (
    suggest_type, Column, Function, Alias, Keyword
)


def sorted_dicts(dicts):
    """input is a list of dicts."""
    return sorted(tuple(x.items()) for x in dicts)


def test_select_suggests_cols_with_visible_table_scope():
    suggestions = suggest_type('SELECT  FROM tabl', 'SELECT ')
    assert suggestions == (
        Column(tables=[(None, 'tabl', None)], drop_unique=None),
        Function(schema=None, filter=None),
        Alias(aliases=['tabl']),
        Keyword(last_token='SELECT'))


def test_select_suggests_cols_with_qualified_table_scope():
    suggestions = suggest_type('SELECT  FROM sch.tabl', 'SELECT ')
    assert suggestions == (
        Column(tables=[('sch', 'tabl', None)], drop_unique=None),
        Function(schema=None, filter=None),
        Alias(aliases=['tabl']),
        Keyword(last_token='SELECT'))


@pytest.mark.parametrize('expression', [
    'SELECT * FROM tabl WHERE ',
    'SELECT * FROM tabl WHERE (',
    'SELECT * FROM tabl WHERE foo = ',
    'SELECT * FROM tabl WHERE bar OR ',
    'SELECT * FROM tabl WHERE foo = 1 AND ',
    'SELECT * FROM tabl WHERE (bar > 10 AND ',
    'SELECT * FROM tabl WHERE (bar AND (baz OR (qux AND (',
    'SELECT * FROM tabl WHERE 10 < ',
    'SELECT * FROM tabl WHERE foo BETWEEN ',
    'SELECT * FROM tabl WHERE foo BETWEEN foo AND ',
])
def test_where_suggests_columns_functions(expression):
    suggestions = suggest_type(expression, expression)
    assert suggestions == (
        Column(tables=[(None, 'tabl', None)], drop_unique=None),
        Function(schema=None, filter=None),
        Alias(aliases=['tabl']),
        Keyword(last_token='WHERE'))
