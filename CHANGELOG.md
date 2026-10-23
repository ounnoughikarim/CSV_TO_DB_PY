# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-10-23

### Bug fixes

- validate config and fall back to example file

- quote SQL identifiers to prevent broken statements and injection

- propagate database write errors instead of logging and continuing

- convert datetime columns on the real dataframe before insert

- adjust datetime conversion test to threshold 0.7

- build connector URLs with URL.create and add missing drivers

- use python-oracledb for oracle connector

- use POSTGRES_DB env var for postgres image

- cast FILTER value to column type

- guard schema drift before truncate and refresh README


### CI

- add ruff jobs to lint and check python code

- publish to PyPI via trusted publishing


### Chores

- add python-related things to ignore

- remove cache

- install ruff as dev dependancies

- install rich (for colored logger)

- remove stale requirements.txt (pyproject.toml is the source of truth)


### Documentation

- add command with --log-level in README.md

- update README for module launch, files_dir, batch_size default and db drivers


### Features

- add a logger and use it

- support --log-level and remove dead polars_type_to_sql

- split library core from CLI entry point

- publish to GitHub Packages and document CLI usage

- support mysql, mssql and oracle dialects


### Performance

- only detect csv delimiter when not configured


### Refactor

- run `ruff check --fix` and `ruff format`

- fix F401 errors

- use absolute csv_to_db_py.* imports

- pass config values as explicit parameters


### Tests

- replace print-scripts with real pytest tests and run them in CI


