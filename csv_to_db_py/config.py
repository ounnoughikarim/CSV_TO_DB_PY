import json
import os

SUPPORTED_DB_TYPES = {"postgres", "mysql", "mssql", "oracle"}


def validate_config(cfg: dict) -> None:
    db_config = cfg.get("DATABASE_CONFIG")
    if db_config is None:
        raise ValueError("config is missing required key 'DATABASE_CONFIG'")
    db_type = db_config.get("type")
    if db_type not in SUPPORTED_DB_TYPES:
        raise ValueError(
            "config 'DATABASE_CONFIG.type' must be one of "
            + ", ".join(sorted(SUPPORTED_DB_TYPES))
            + f", got {db_type!r}"
        )
    if "files_dir" not in cfg:
        raise ValueError("config is missing required key 'files_dir'")


script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "..", "mainConfig.json")
fallback_path = os.path.join(script_dir, "..", "mainConfig.json.example-strict")
try:
    with open(config_path, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    with open(fallback_path, "r") as f:
        config = json.load(f)

validate_config(config)

PG_RESERVED = {
    "insert",
    "delete",
    "update",
    "select",
    "drop",
    "and",
    "or",
    "from",
    "create",
    "join",
    "limit",
    "table",
    "order",
    "user",
    "not",
    "where",
    "group",
}
