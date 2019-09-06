import functools
import io
import os

import pytest

from .. import cli
from .factories import LogEntryFactory


_TEST_LOG_DIR = os.path.dirname(__file__)


@pytest.fixture
def log_entry_factory():
    return LogEntryFactory()


@pytest.fixture
def log_path():
    return functools.partial(
        os.path.join,
        _TEST_LOG_DIR,
    )


@pytest.fixture
def log_analyzer_main(capsys, mocker):
    # Configuring logging breaks pytest
    setup_logging_mock = mocker.patch('log_analyzer.cli.setup_logging')

    def main_impl(*args):
        mocker.patch('sys.argv', ('log_analyzer',) + args)

        setup_logging_mock.reset_mock()

        cli.main()

        setup_logging_mock.assert_called_once_with(mocker.ANY)

        return io.StringIO(capsys.readouterr().out)

    return main_impl
