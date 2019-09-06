from __future__ import annotations

import argparse
import logging
import sys

import importlib_metadata

from . import (
    analyze,
    convert,
    logfile,
)

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


LOG_LEVELS = (
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
)


def main():
    argparser = create_argparser()
    args = argparser.parse_args()

    setup_logging(args.log_level.upper())
    _logger.debug('Log analyzer configured. Running..')

    args.main(args)


def create_argparser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser('Log Analyzer')

    def print_help(args: argparse.Namespace) -> None:  # pylint: disable=unused-argument
        arg_parser.print_help()
        sys.exit(1)

    arg_parser.set_defaults(main=print_help)

    arg_parser.add_argument(
        '--version',
        action='version',
        version=importlib_metadata.version('mk-log-analyzer'),
    )

    log_level_choices = []
    for log_level in LOG_LEVELS:
        log_level_choices.append(logging.getLevelName(log_level).lower())

    arg_parser.add_argument(
        '--log-level',
        choices=log_level_choices,
        default=logging.getLevelName(LOG_LEVELS[0]).lower(),
        help='Set log level. Default: %(default)s',
    )

    subparsers = arg_parser.add_subparsers(title='Command')
    add_stats_arguments(subparsers.add_parser('stats', help='Show statistics from a log file'))
    add_convert_arguments(subparsers.add_parser('convert', help='Convert log file'))

    return arg_parser


def add_stats_arguments(arg_parser: argparse.ArgumentParser) -> None:
    arg_parser.set_defaults(main=stats_main)

    arg_parser.add_argument(
        'log_file',
        help='Path to log file'
    )


def stats_main(args: argparse.Namespace) -> None:
    stats = analyze.get_stats(args.log_file)

    print(args.log_file)
    print(f'  Messages: {stats.message_count}')
    print(f'  Invalid log entries: {stats.invalid_log_entry_count}')

    print('  Message type counts:')
    for message_type, message_count in stats.message_counts_by_type.items():
        print(f'    {message_type: <20} {message_count: >6}')


def add_convert_arguments(arg_parser: argparse.ArgumentParser) -> None:
    arg_parser.set_defaults(main=convert_main)

    arg_parser.add_argument(
        '--extract-containers',
        help='Extract messages from container messages',
        default=False,
        action='store_true',
    )

    arg_parser.add_argument(
        '--preserve-containers',
        help='Preserve container messages when extracting messages',
        default=False,
        action='store_true',
    )

    arg_parser.add_argument(
        '--annotate-extracted',
        help='Annotate boundaries of extracted container messages',
        default=False,
        action='store_true',
    )

    arg_parser.add_argument(
        '--filter-messages',
        dest='message_types',
        help='Only include messages of given types',
        default=[],
        action='append',
    )

    arg_parser.add_argument(
        '--filter-messagers',
        dest='messagers',
        help='Only include messages sent by or sent to the given messagers',
        default=set(),
        action=MessagerFilterAction,
    )

    arg_parser.add_argument(
        'source_path',
        help='Path to source log file'
    )

    arg_parser.add_argument(
        '--output',
        '-o',
        help='Path to file to write the result. If not set, the result is written to stdout'
    )


def convert_main(args: argparse.Namespace) -> None:
    log_entries = logfile.parse(args.source_path)

    if args.extract_containers:
        log_entries = convert.extract_container_messages(
            log_entries,
            preserve_container=args.preserve_containers,
            annotate_extracted=args.annotate_extracted,
        )

    if args.message_types:
        log_entries = convert.filter_by_messages(log_entries, args.message_types)

    if args.messagers:
        log_entries = convert.filter_by_messagers(log_entries, args.messagers)

    output_file = (
        open(args.output, 'wt')
        if args.output
        else sys.stdout
    )
    logfile.save_as_json_log(log_entries, output_file)


def setup_logging(log_level: str) -> None:
    handler = logging.StreamHandler(sys.stderr)

    handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(message)s [%(name)s : %(lineno)s]'))

    logger = logging.getLogger(__package__)
    logger.propagate = False
    logger.addHandler(handler)
    logger.setLevel(log_level)


class MessagerFilterAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        try:
            getattr(namespace, self.dest).add(int(value))

        except ValueError as err:
            raise argparse.ArgumentError(self, f'"{value}" is not a number') from err
