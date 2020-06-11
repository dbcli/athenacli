# -*- coding: utf-8 -*-
import os
import sys
import select
import click
import threading
import logging
import itertools
import sqlparse
import traceback
from time import time
from datetime import datetime
from random import choice
from collections import namedtuple

from prompt_toolkit.completion import DynamicCompleter
from prompt_toolkit.shortcuts import PromptSession, CompleteStyle
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.history import FileHistory
from prompt_toolkit.document import Document
from prompt_toolkit.layout.processors import (
    HighlightMatchingBracketProcessor,
    ConditionalProcessor)
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.filters import HasFocus, IsDone
from prompt_toolkit.enums import DEFAULT_BUFFER, EditingMode
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pygments.lexers.sql import SqlLexer
from cli_helpers.tabular_output import TabularOutputFormatter
from cli_helpers.tabular_output import preprocessors
from pyathena.error import OperationalError

import athenacli.packages.special as special
from athenacli.sqlexecute import SQLExecute
from athenacli.completer import AthenaCompleter
from athenacli.style import AthenaStyle
from athenacli.completion_refresher import CompletionRefresher
from athenacli.packages.tabular_output import sql_format
from athenacli.clistyle import style_factory, style_factory_output
from athenacli.packages.prompt_utils import confirm, confirm_destructive_query
from athenacli.key_bindings import cli_bindings
from athenacli.clitoolbar import create_toolbar_tokens_func
from athenacli.lexer import Lexer
from athenacli.clibuffer import cli_is_multiline
from athenacli.sqlexecute import SQLExecute
from athenacli.config import read_config_files, write_default_config, mkdir_p, AWSConfig


# Query tuples are used for maintaining history
Query = namedtuple('Query', ['query', 'successful', 'mutating'])

LOGGER = logging.getLogger(__name__)
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
ATHENACLIRC = '~/.athenacli/athenaclirc'
DEFAULT_CONFIG_FILE = os.path.join(PACKAGE_ROOT, 'athenaclirc')


class AthenaCli(object):
    DEFAULT_PROMPT = '\\d@\\r> '
    MAX_LEN_PROMPT = 45

    def __init__(self, region, aws_access_key_id, aws_secret_access_key,
                 s3_staging_dir, athenaclirc, profile, database):

        config_files = [DEFAULT_CONFIG_FILE]
        if os.path.exists(os.path.expanduser(athenaclirc)):
            config_files.append(athenaclirc)
        _cfg = self.config = read_config_files(config_files)

        self.init_logging(_cfg['main']['log_file'], _cfg['main']['log_level'])

        aws_config = AWSConfig(
            aws_access_key_id, aws_secret_access_key, region, s3_staging_dir, profile, _cfg
        )

        try:
            self.connect(aws_config, database)
        except Exception as e:
            self.echo(str(e), err=True, fg='red')
            err_msg = '''
There was an error while connecting to AWS Athena. It could be caused due to
missing/incomplete configuration. Please verify the configuration in %s
and run athenacli again.

For more details about the error, you can check the log file: %s''' % (athenaclirc, _cfg['main']['log_file'])
            self.echo(err_msg)
            LOGGER.exception('error: %r', e)
            sys.exit(1)

        special.set_timing_enabled(_cfg['main'].as_bool('timing'))
        self.multi_line = _cfg['main'].as_bool('multi_line')
        self.key_bindings = _cfg['main']['key_bindings']
        self.prompt = _cfg['main']['prompt'] or self.DEFAULT_PROMPT
        self.destructive_warning = _cfg['main']['destructive_warning']
        self.syntax_style = _cfg['main']['syntax_style']
        self.prompt_continuation_format = _cfg['main']['prompt_continuation']

        self.formatter = TabularOutputFormatter(_cfg['main']['table_format'])
        self.formatter.cli = self
        sql_format.register_new_formatter(self.formatter)

        self.cli_style = _cfg['colors']
        self.output_style = style_factory_output(self.syntax_style, self.cli_style)

        self.completer = AthenaCompleter()
        self._completer_lock = threading.Lock()
        self.completion_refresher = CompletionRefresher()

        self.prompt_app = None

        self.query_history = []
        # Register custom special commands.
        self.register_special_commands()

    def init_logging(self, log_file, log_level_str):
        file_path = os.path.expanduser(log_file)
        if not os.path.exists(file_path):
            mkdir_p(os.path.dirname(file_path))

        handler = logging.FileHandler(os.path.expanduser(log_file))
        log_level_map = {
            'CRITICAL': logging.CRITICAL,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
        }

        log_level = log_level_map[log_level_str.upper()]

        formatter = logging.Formatter(
            '%(asctime)s (%(process)d/%(threadName)s) '
            '%(name)s %(levelname)s - %(message)s')

        handler.setFormatter(formatter)

        LOGGER.addHandler(handler)
        LOGGER.setLevel(log_level)

        root_logger = logging.getLogger('athenacli')
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level)

        root_logger.debug('Initializing athenacli logging.')
        root_logger.debug('Log file %r.', log_file)

        pgspecial_logger = logging.getLogger('special')
        pgspecial_logger.addHandler(handler)
        pgspecial_logger.setLevel(log_level)

    def register_special_commands(self):
        special.register_special_command(
            self.change_db, 'use', '\\u',
            'Change to a new database.', aliases=('\\u',))
        special.register_special_command(
            self.change_prompt_format, 'prompt', '\\R',
            'Change prompt format.', aliases=('\\R',), case_sensitive=True)
        special.register_special_command(
            self.change_table_format, 'tableformat', '\\T',
            'Change the table format used to output results.',
            aliases=('\\T',), case_sensitive=True)

    def change_table_format(self, arg, **_):
        try:
            self.formatter.format_name = arg
            yield (None, None, None,
                   'Changed table format to {}'.format(arg))
        except ValueError:
            msg = 'Table format {} not recognized. Allowed formats:'.format(
                arg)
            for table_type in self.formatter.supported_formats:
                msg += "\n\t{}".format(table_type)
            yield (None, None, None, msg)

    def change_db(self, arg, **_):
        if arg is None:
            self.sqlexecute.connect()
        else:
            self.sqlexecute.connect(database=arg)

        yield (None, None, None, 'You are now connected to database "%s"' % self.sqlexecute.database)

    def change_prompt_format(self, arg, **_):
        """
        Change the prompt format.
        """
        if not arg:
            message = 'Missing required argument, format.'
            return [(None, None, None, message)]

        self.prompt = self.get_prompt(arg)
        return [(None, None, None, "Changed prompt format to %s" % arg)]

    def connect(self, aws_config, database):
        self.sqlexecute = SQLExecute(
            aws_access_key_id = aws_config.aws_access_key_id,
            aws_secret_access_key = aws_config.aws_secret_access_key,
            region_name = aws_config.region,
            s3_staging_dir = aws_config.s3_staging_dir,
            role_arn = aws_config.role_arn,
            database = database
        )

    def handle_editor_command(self, text):
        """
        Editor command is any query that is prefixed or suffixed
        by a '\e'. The reason for a while loop is because a user
        might edit a query multiple times.
        For eg:
        "select * from \e"<enter> to edit it in vim, then come
        back to the prompt with the edited query "select * from
        blah where q = 'abc'\e" to edit it again.
        :param text: str
        :return: Document
        """
        while special.editor_command(text):
            filename = special.get_filename(text)
            query = (special.get_editor_query(text) or
                     self.get_last_query())
            sql, message = special.open_external_editor(filename, sql=query)
            if message:
                # Something went wrong. Raise an exception and bail.
                raise RuntimeError(message)
            while True:
                try:
                    text = self.prompt_app.prompt(default=sql)
                    break
                except KeyboardInterrupt:
                    sql = ''
            continue
        return text

    def run_query(self, query, new_line=True):
        """Runs *query*."""
        if (self.destructive_warning and
                confirm_destructive_query(query) is False):
            message = 'Wise choice. Command execution stopped.'
            click.echo(message)
            return

        results = self.sqlexecute.run(query)
        for result in results:
            title, rows, headers, _ = result
            self.formatter.query = query
            output = self.format_output(title, rows, headers)
            for line in output:
                click.echo(line, nl=new_line)

    def run_cli(self):
        self.iterations = 0
        self.configure_pager()
        self.refresh_completions()

        history_file = os.path.expanduser(self.config['main']['history_file'])
        history = FileHistory(history_file)
        self._build_prompt_app(history)

        def one_iteration():
            try:
                text = self.prompt_app.prompt()
            except KeyboardInterrupt:
                return

            special.set_expanded_output(False)
            try:
                text = self.handle_editor_command(text)
            except RuntimeError as e:
                LOGGER.error("sql: %r, error: %r", text, e)
                LOGGER.error("traceback: %r", traceback.format_exc())
                self.echo(str(e), err=True, fg='red')
                return

            if not text.strip():
                return

            if self.destructive_warning:
                destroy = confirm_destructive_query(text)
                if destroy is None:
                    pass  # Query was not destructive. Nothing to do here.
                elif destroy is True:
                    self.echo('Your call!')
                else:
                    self.echo('Wise choice!')
                    return

            mutating = False

            try:
                LOGGER.debug('sql: %r', text)

                special.write_tee(self.get_prompt(self.prompt) + text)
                successful = False
                start = time()
                res = self.sqlexecute.run(text)
                successful = True
                threshold = 1000
                result_count = 0

                for title, rows, headers, status in res:
                    if rows and len(rows) > threshold:
                        self.echo(
                            'The result set has more than {} rows.'.format(threshold),
                            fg='red'
                        )
                        if not confirm('Do you want to continue?'):
                            self.echo('Aborted!', err=True, fg='red')
                            break

                    formatted = self.format_output(
                        title, rows, headers, special.is_expanded_output(), None
                    )

                    t = time() - start
                    try:
                        if result_count > 0:
                            self.echo('')
                        try:
                            self.output(formatted, status)
                        except KeyboardInterrupt:
                            pass

                        if special.is_timing_enabled():
                            self.echo('Time: %0.03fs' % t)
                    except KeyboardInterrupt:
                        pass

                    start = time()
                    result_count += 1
                    mutating = mutating or is_mutating(status)
                special.unset_once_if_written()
            except EOFError as e:
                raise e
            except KeyboardInterrupt:
                pass
            except NotImplementedError:
                self.echo('Not Yet Implemented.', fg="yellow")
            except OperationalError as e:
                LOGGER.debug("Exception: %r", e)
                LOGGER.error("sql: %r, error: %r", text, e)
                LOGGER.error("traceback: %r", traceback.format_exc())
                self.echo(str(e), err=True, fg='red')
            except Exception as e:
                LOGGER.error("sql: %r, error: %r", text, e)
                LOGGER.error("traceback: %r", traceback.format_exc())
                self.echo(str(e), err=True, fg='red')
            else:
                # Refresh the table names and column names if necessary.
                if need_completion_refresh(text):
                    self.refresh_completions()

            query = Query(text, successful, mutating)
            self.query_history.append(query)

        try:
            while True:
                one_iteration()
                self.iterations += 1
        except EOFError:
            special.close_tee()

    def get_output_margin(self, status=None):
        """Get the output margin (number of rows for the prompt, footer and
        timing message."""
        margin = self.get_reserved_space() + self.get_prompt(self.prompt).count('\n') + 1
        if special.is_timing_enabled():
            margin += 1
        if status:
            margin += 1 + status.count('\n')

        return margin

    def output(self, output, status=None):
        """Output text to stdout or a pager command.
        The status text is not outputted to pager or files.
        The message will be logged in the audit log, if enabled. The
        message will be written to the tee file, if enabled. The
        message will be written to the output file, if enabled.
        """
        if output:
            size = self.prompt_app.output.get_size()

            margin = self.get_output_margin(status)

            fits = True
            buf = []
            output_via_pager = self.explicit_pager and special.is_pager_enabled()
            for i, line in enumerate(output, 1):
                special.write_tee(line)
                special.write_once(line)

                if fits or output_via_pager:
                    # buffering
                    buf.append(line)
                    if len(line) > size.columns or i > (size.rows - margin):
                        fits = False
                        if not self.explicit_pager and special.is_pager_enabled():
                            # doesn't fit, use pager
                            output_via_pager = True

                        if not output_via_pager:
                            # doesn't fit, flush buffer
                            for line in buf:
                                click.secho(line)
                            buf = []
                else:
                    click.secho(line)

            if buf:
                if output_via_pager:
                    # sadly click.echo_via_pager doesn't accept generators
                    click.echo_via_pager("\n".join(buf))
                else:
                    for line in buf:
                        click.secho(line)

        if status:
            click.secho(status)

    def configure_pager(self):
        self.explicit_pager = False

        if not self.config['main'].as_bool('enable_pager'):
            special.disable_pager()

    def format_output(self, title, cur, headers, expanded=False,
                      max_width=None):
        expanded = expanded or self.formatter.format_name == 'vertical'
        output = []

        output_kwargs = {
            'disable_numparse': True,
            'preserve_whitespace': True,
            'preprocessors': (preprocessors.align_decimals, ),
            'style': self.output_style
        }

        if title:  # Only print the title if it's not None.
            output = itertools.chain(output, [title])

        if cur:
            column_types = None
            if hasattr(cur, 'description'):
                column_types = [str for col in cur.description]

            if max_width is not None:
                cur = list(cur)

            formatted = self.formatter.format_output(
                cur, headers, format_name='vertical' if expanded else None,
                column_types=column_types,
                **output_kwargs)

            if isinstance(formatted, str):
                formatted = formatted.splitlines()
            formatted = iter(formatted)

            first_line = next(formatted)
            formatted = itertools.chain([first_line], formatted)

            if (not expanded and max_width and headers and cur and
                    len(first_line) > max_width):
                formatted = self.formatter.format_output(
                    cur, headers, format_name='vertical', column_types=column_types, **output_kwargs)
                if isinstance(formatted, str):
                    formatted = iter(formatted.splitlines())

            output = itertools.chain(output, formatted)

        return output

    def echo(self, s, **kwargs):
        """Print a message to stdout.
        The message will be logged in the audit log, if enabled.
        All keyword arguments are passed to click.echo().
        """
        click.secho(s, **kwargs)

    def refresh_completions(self):
        with self._completer_lock:
            self.completer.reset_completions()

        completer_options = {
            'smart_completion': True,
            'supported_formats': self.formatter.supported_formats,
            'keyword_casing': self.completer.keyword_casing
        }
        self.completion_refresher.refresh(
            self.sqlexecute,
            self._on_completions_refreshed,
            completer_options
        )

    def _on_completions_refreshed(self, new_completer):
        """Swap the completer object in cli with the newly created completer.
        """
        with self._completer_lock:
            self.completer = new_completer

        if self.prompt_app:
            # After refreshing, redraw the CLI to clear the statusbar
            # "Refreshing completions..." indicator
            self.prompt_app.app.invalidate()

    def _build_prompt_app(self, history):
        key_bindings = cli_bindings(self)

        def get_message():
            prompt = self.get_prompt(self.prompt)
            if len(prompt) > self.MAX_LEN_PROMPT:
                prompt = self.get_prompt('\\r:\\d> ')
            return [('class:prompt', prompt)]

        def get_continuation(width, line_number, is_soft_wrap):
            continuation = ' ' * (width -1) + ' '
            return [('class:continuation', continuation)]

        def show_suggestion_tip():
            return self.iterations < 2

        get_toolbar_tokens = create_toolbar_tokens_func(
            self, show_suggestion_tip)

        with self._completer_lock:
            if self.key_bindings == 'vi':
                editing_mode = EditingMode.VI
            else:
                editing_mode = EditingMode.EMACS

            self.prompt_app = PromptSession(
                lexer=PygmentsLexer(Lexer),
                reserve_space_for_menu=self.get_reserved_space(),
                message=get_message,
                prompt_continuation=get_continuation,
                bottom_toolbar=get_toolbar_tokens,
                complete_style=CompleteStyle.COLUMN,
                input_processors=[ConditionalProcessor(
                    processor=HighlightMatchingBracketProcessor(
                        chars='[](){}'),
                    filter=HasFocus(DEFAULT_BUFFER) & ~IsDone()
                )],
                tempfile_suffix='.sql',
                completer=DynamicCompleter(lambda: self.completer),
                history=history,
                auto_suggest=AutoSuggestFromHistory(),
                complete_while_typing=True,
                multiline=cli_is_multiline(self),
                style=style_factory(self.syntax_style, self.cli_style),
                include_default_pygments_style=False,
                key_bindings=key_bindings,
                enable_open_in_editor=True,
                enable_system_prompt=True,
                editing_mode=editing_mode,
                search_ignore_case=True
            )

    def get_prompt(self, string):
        sqlexecute = self.sqlexecute
        now = datetime.now()
        string = string.replace('\\r', sqlexecute.region_name or '(none)')
        string = string.replace('\\d', sqlexecute.database or '(none)')
        string = string.replace('\\n', "\n")
        string = string.replace('\\D', now.strftime('%a %b %d %H:%M:%S %Y'))
        string = string.replace('\\m', now.strftime('%M'))
        string = string.replace('\\P', now.strftime('%p'))
        string = string.replace('\\R', now.strftime('%H'))
        string = string.replace('\\s', now.strftime('%S'))
        return string

    def get_reserved_space(self):
        """Get the number of lines to reserve for the completion menu."""
        reserved_space_ratio = .45
        max_reserved_space = 8
        _, height = click.get_terminal_size()
        return min(int(round(height * reserved_space_ratio)), max_reserved_space)

    def get_last_query(self):
        """Get the last query executed or None."""
        return self.query_history[-1][0] if self.query_history else None


def need_completion_refresh(queries):
    """Determines if the completion needs a refresh by checking if the sql
    statement is an alter, create, drop or change db."""
    tokens = {
        'use', '\\u',
        'create',
        'drop'
    }

    for query in sqlparse.split(queries):
        try:
            first_token = query.split()[0]
            if first_token.lower() in tokens:
                return True
        except Exception:
            return False


def is_mutating(status):
    """Determines if the statement is mutating based on the status."""
    if not status:
        return False

    mutating = set(['insert', 'update', 'delete', 'alter', 'create', 'drop',
                    'replace', 'truncate', 'load'])
    return status.split(None, 1)[0].lower() in mutating

@click.command()
@click.option('-e', '--execute', type=str, help='Execute a command (or a file) and quit.')
@click.option('-r', '--region', type=str, help="AWS region.")
@click.option('--aws-access-key-id', type=str, help="AWS access key id.")
@click.option('--aws-secret-access-key', type=str, help="AWS secretaccess key.")
@click.option('--s3-staging-dir', type=str, help="Amazon S3 staging directory where query results are stored.")
@click.option('--athenaclirc', default=ATHENACLIRC, type=click.Path(dir_okay=False), help="Location of athenaclirc file.")
@click.option('--profile', type=str, default='default', help='AWS profile')
@click.argument('database', default='default', nargs=1)
def cli(execute, region, aws_access_key_id, aws_secret_access_key,
        s3_staging_dir, athenaclirc, profile, database):
    '''A Athena terminal client with auto-completion and syntax highlighting.

    \b
    Examples:
      - athenacli
      - athenacli my_database
    '''
    if (athenaclirc == ATHENACLIRC) and (not os.path.exists(os.path.expanduser(athenaclirc))):
        err_msg = '''
        Welcome to athenacli!

        It seems this is your first time to run athenacli,
        we generated a default config file for you
            %s
        Please change it accordingly, and run athenacli again.
        ''' % athenaclirc
        print(err_msg)
        write_default_config(DEFAULT_CONFIG_FILE, athenaclirc)
        sys.exit(1)

    if profile != 'default':
        os.environ['AWS_PROFILE'] = profile

    athenacli = AthenaCli(
        region=region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key= aws_secret_access_key,
        s3_staging_dir=s3_staging_dir,
        athenaclirc=athenaclirc,
        profile=profile,
        database=database
    )

    #  --execute argument
    if execute:
        if execute == '-':
            if select.select([sys.stdin, ], [], [], 0.0)[0]:
                query = sys.stdin.read()
            else:
                raise RuntimeError("No query to execute on stdin")
        elif os.path.exists(execute):
            with open(execute) as f:
                query = f.read()
        else:
            query = execute
        try:
            athenacli.formatter.format_name = 'csv'
            athenacli.run_query(query)
            exit(0)
        except Exception as e:
            click.secho(str(e), err=True, fg='red')
            exit(1)

    athenacli.run_cli()


if __name__ == '__main__':
    cli()
