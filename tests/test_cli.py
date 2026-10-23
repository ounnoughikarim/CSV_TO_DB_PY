import pytest

from csv_to_db_py.main import parse_args


def test_parse_args_with_config_and_input():
    args = parse_args(["--config", "c.json", "x.csv"])
    assert args.config == "c.json"
    assert args.input_path == "x.csv"


def test_parse_args_defaults():
    args = parse_args([])
    assert args.input_path is None
    assert args.config == "mainConfig.json"
    assert args.log_level == "info"


def test_parse_args_invalid_log_level():
    with pytest.raises(SystemExit):
        parse_args(["--log-level", "nope"])
