# encoding: utf-8

import logging
import sqlparse
import pyathena

from athenacli.packages import special

logger = logging.getLogger(__name__)


class SQLExecute(object):
    DATABASES_QUERY = 'SHOW DATABASES'
    TABLES_QUERY = 'SHOW TABLES'
    TABLE_COLUMNS_QUERY = '''
        SELECT table_name, column_name FROM information_schema.columns
        WHERE table_schema = '%s'
        ORDER BY table_name, ordinal_position
    '''

    def __init__(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        region_name,
        s3_staging_dir,
        database
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.s3_staging_dir = s3_staging_dir
        self.database = database

        self.connect()

    def connect(self, database=None):
        conn = pyathena.connect(
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key,
            region_name = self.region_name,
            s3_staging_dir = self.s3_staging_dir,
            schema_name = database or self.database
        )
        self.database = database or self.database

        if hasattr(self, 'conn'):
            self.conn.close()
        self.conn = conn

    def run(self, statement):
        '''Execute the sql in the database and return the results.

        The results are a list of tuples. Each tuple has 4 values
        (title, rows, headers, status).
        '''
        # Remove spaces and EOL
        statement = statement.strip()
        if not statement:  # Empty string
            yield (None, None, None, None)

        # Split the sql into separate queries and run each one.
        components = sqlparse.split(statement)

        for sql in components:
            # Remove spaces, eol and semi-colons.
            sql = sql.rstrip(';')

            # \G is treated specially since we have to set the expanded output.
            if sql.endswith('\\G'):
                special.set_expanded_output(True)
                sql = sql[:-2].strip()

            cur = self.conn.cursor()

            try:
                for result in special.execute(cur, sql):
                    yield result
            except special.CommandNotFound:  # Regular SQL
                cur.execute(sql)
                yield self.get_result(cur)

    def get_result(self, cursor):
        '''Get the current result's data from the cursor.'''
        title = headers = None

        # cursor.description is not None for queries that return result sets,
        # e.g. SELECT or SHOW.
        if cursor.description is not None:
            headers = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            status = '%d row%s in set' % (len(rows), '' if len(rows) == 1 else 's')
        else:
            logger.debug('No rows in result.')
            rows = None
            status = 'Query OK'
        return (title, rows, headers, status)

    def tables(self):
        '''Yields table names.'''
        with self.conn.cursor() as cur:
            cur.execute(self.TABLES_QUERY)
            for row in cur:
                yield row

    def table_columns(self):
        '''Yields column names.'''
        with self.conn.cursor() as cur:
            cur.execute(self.TABLE_COLUMNS_QUERY % self.database)
            for row in cur:
                yield row

    def databases(self):
        with self.conn.cursor() as cur:
            cur.execute(self.DATABASES_QUERY)
            return [x[0] for x in cur.fetchall()]
