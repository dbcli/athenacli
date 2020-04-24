# -*- coding: utf-8 -*-


def format_status(rows_length=None, cursor=None):
    return rows_status(rows_length) + statistics(cursor)

def rows_status(rows_length):
    if rows_length:
        return '%d row%s in set' % (rows_length, '' if rows_length == 1 else 's')
    else:
        return 'Query OK'

def statistics(cursor):
    if cursor:
        # Most regions are $5 per TB: https://aws.amazon.com/athena/pricing/
        approx_cost = cursor.data_scanned_in_bytes / (1024 ** 4) * 5

        return '\nExecution time: %d ms, Data scanned: %s, Approximate cost: $%.2f' % (
                cursor.execution_time_in_millis,
                humanize_size(cursor.data_scanned_in_bytes),
                approx_cost)
    else:
        return ''

def humanize_size(num_bytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']

    suffix_index = 0
    while num_bytes >= 1024 and suffix_index < len(suffixes) - 1:
        num_bytes /= 1024.0
        suffix_index += 1

    num = ('%.2f' % num_bytes).rstrip('0').rstrip('.')
    return '%s %s' % (num, suffixes[suffix_index])
