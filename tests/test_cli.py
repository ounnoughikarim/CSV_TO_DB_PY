import pytest

from csv_to_db_py.main import parse_args


def test_parse_args_with_log_level_and_input():
    args = parse_args(["--log-level", "debug", "x.csv"])
    assert args.log_level == "debug"
    assert args.input_path == "x.csv"


def test_parse_args_defaults():
    args = parse_args([])
    assert args.input_path is None
    assert args.log_level == "info"


def test_parse_args_with_input_only():
    args = parse_args(["data.csv"])
    assert args.input_path == "data.csv"


def test_parse_args_invalid_log_level():
    with pytest.raises(SystemExit):
        parse_args(["--log-level", "nope"])
