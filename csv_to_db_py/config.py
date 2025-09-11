import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "..", "mainConfig.json")
with open(config_path, "r") as f:
    config = json.load(f)

PG_RESERVED= {
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
        "group"
}