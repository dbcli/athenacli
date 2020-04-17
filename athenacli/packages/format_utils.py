# -*- coding: utf-8 -*-


def format_status(rows_length):
    if rows_length:
        return '%d row%s in set' % (rows_length, '' if rows_length == 1 else 's')
    else:
        return 'Query OK'
