import argparse
import sys

from csv_to_db_py.config import load_config
from csv_to_db_py.core import load_csv_to_db
from csv_to_db_py.logger import set_logger


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="csv-to-db",
        description="Load CSV/XLSX files into a database table",
    )
    parser.add_argument("input_path", nargs="?", default=None)
    parser.add_argument("--config", default="mainConfig.json")
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    set_logger(args.log_level)
    cfg = load_config(args.config)
    load_csv_to_db(cfg, args.input_path)


if __name__ == "__main__":
    main()
