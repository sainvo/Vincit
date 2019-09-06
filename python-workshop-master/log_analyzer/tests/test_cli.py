import argparse

import pytest

from .. import cli


def test_argparser(mocker):
    parser = cli.create_argparser()

    assert isinstance(parser, argparse.ArgumentParser)

    args = parser.parse_args(['stats', 'foo.log'])
    assert args.main is cli.stats_main
    assert args.log_file == 'foo.log'
    assert args.log_level == 'warning'

    args = parser.parse_args(['--log-level=info', 'stats', 'bar.log'])
    assert args.main is cli.stats_main
    assert args.log_file == 'bar.log'
    assert args.log_level == 'info'

    args = parser.parse_args(['convert', 'test.log'])
    assert args.main is cli.convert_main
    assert args.source_path == 'test.log'
    assert args.output is None
    assert not args.extract_containers
    assert not args.preserve_containers
    assert not args.annotate_extracted
    assert not args.message_types
    assert not args.messagers
    assert args.log_level == 'warning'

    args = parser.parse_args([
        'convert',
        '--filter-messagers=1',
        '--filter-messagers=2',
        '--extract-containers',
        'test.log',
    ])
    assert args.main is cli.convert_main
    assert args.source_path == 'test.log'
    assert args.output is None
    assert args.extract_containers
    assert not args.preserve_containers
    assert not args.annotate_extracted
    assert not args.message_types
    assert args.messagers == {1, 2}
    assert args.log_level == 'warning'

    with pytest.raises(SystemExit):
        args = parser.parse_args([
            'convert',
            '--filter-messagers=a',
            'test.log',
        ])

    parser.print_help = mocker.Mock()
    args = parser.parse_args([])

    with pytest.raises(SystemExit):
        args.main(args)

    parser.print_help.assert_called_once_with()


def test_stats(log_analyzer_main, log_path):
    log_file_path = log_path('log_ping_pong.log')

    stdout = log_analyzer_main('stats', log_file_path)

    lines = list(stdout.getvalue().split('\n'))
    assert lines == [
        log_file_path,
        '  Messages: 4',
        '  Invalid log entries: 0',
        '  Message type counts:',
        '    ping                      2',
        '    pong                      2',
        '',
    ]


@pytest.mark.parametrize(
    'args, source_log, expected_log',
    (
        (
            (),
            'log_ping_pong_with_container.log',
            'log_ping_pong_with_container.jsonlog',
        ),
        (
            ('--extract-containers',),
            'log_ping_pong_with_container.log',
            'log_ping_pong_with_container_expanded.jsonlog',
        ),
        (
            ('--extract-containers', '--annotate-extracted'),
            'log_ping_pong_with_container.log',
            'log_ping_pong_with_container_expanded_and_annotated.jsonlog',
        ),
        (
            ('--extract-containers', '--preserve-containers'),
            'log_ping_pong_with_container.log',
            'log_ping_pong_with_container_expanded_and_preserved.jsonlog',
        ),
        (
            ('--extract-containers', '--preserve-containers'),
            'log_ping_pong_with_container.log',
            'log_ping_pong_with_container_expanded_and_preserved.jsonlog',
        ),
        (
            ('--filter-messagers=1', '--filter-messagers=2'),
            'log_ping_pong_with_container_expanded_and_preserved.jsonlog',
            'log_ping_pong_with_container_expanded_and_preserved_filtered1.jsonlog',
        ),
        (
            ('--filter-messages=ping', '--filter-messages=container'),
            'log_ping_pong_with_container_expanded_and_preserved.jsonlog',
            'log_ping_pong_with_container_expanded_and_preserved_filtered2.jsonlog',
        ),
    ),
)
def test_convert_ping_pong_with_container_log(log_analyzer_main, log_path, args, source_log, expected_log):
    source_log_path = log_path(source_log)

    stdout = log_analyzer_main('convert', *args, source_log_path)

    with open(log_path(expected_log), 'rt') as expected_log_file:
        assert list(stdout) == list(expected_log_file)


def test_setup_logging(mocker):
    get_logger_mock = mocker.patch('logging.getLogger')
    logger_mock = get_logger_mock.return_value

    cli.setup_logging(mocker.sentinel.loglevel)

    logger_mock.setLevel.assert_called_once_with(mocker.sentinel.loglevel)
    assert not logger_mock.propagate

    logger_mock.addHandler.assert_called_once_with(mocker.ANY)
    handler = logger_mock.addHandler.call_args_list[0][0]
    assert handler is not None
