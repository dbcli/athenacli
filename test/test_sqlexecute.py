from unittest.mock import Mock, patch

import pytest

from athenacli.completion_refresher import CompletionRefresher
from athenacli.sqlexecute import SQLExecute


@pytest.fixture
def connection_factory():
    with patch('athenacli.sqlexecute.pyathena.connect') as connect:
        yield connect


def executor(database):
    return SQLExecute('key', 'secret', 'token', 'us-east-1',
                      's3://test-results/', 'primary', None, database)


def test_catalog_survives_database_changes(connection_factory):
    sql = executor('custom.analytics')
    assert connection_factory.call_args.kwargs['catalog_name'] == 'custom'
    sql.connect('other.reporting')
    assert sql.catalog_name == 'other'
    assert sql.database == 'reporting'
    sql.connect('archive')
    assert connection_factory.call_args.kwargs['catalog_name'] == 'other'
    assert connection_factory.call_args.kwargs['schema_name'] == 'archive'
    sql.connect()
    assert connection_factory.call_args.kwargs['catalog_name'] == 'other'


def test_refresh_uses_selected_catalog(connection_factory):
    sql = executor('custom.analytics')
    refresher = CompletionRefresher()
    refresher.refreshers = {}
    callback = Mock()
    refresher._bg_refresh(sql, callback, {})
    assert connection_factory.call_args.kwargs['catalog_name'] == 'custom'
    assert connection_factory.call_args.kwargs['schema_name'] == 'analytics'
    callback.assert_called_once()


def test_default_catalog_unchanged(connection_factory):
    sql = executor('analytics')
    assert sql.catalog_name == 'AwsDataCatalog'
    assert connection_factory.call_args.kwargs['catalog_name'] == 'AwsDataCatalog'


def test_failed_connection_keeps_catalog_and_database(connection_factory):
    sql = executor('custom.analytics')
    original_connection = sql.conn
    connection_factory.side_effect = RuntimeError('connection failed')
    with pytest.raises(RuntimeError, match='connection failed'):
        sql.connect('other.reporting')
    assert sql.catalog_name == 'custom'
    assert sql.database == 'analytics'
    assert sql.conn is original_connection
