"""Release tooling: bump the version, update the changelog and tag a release."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"
BUMP_TYPES = ("patch", "minor", "major")

VERSION_RE = re.compile(r'^version = "([^"]+)"', re.MULTILINE)
BREAKING_RE = re.compile(r"^[a-z]+(?:\([^)]*\))?!:", re.IGNORECASE)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()


def current_version() -> str:
    match = VERSION_RE.search(PYPROJECT.read_text())
    if match is None:
        raise SystemExit(f"no version found in {PYPROJECT}")
    return match.group(1)


def messages_since_last_tag() -> list[str]:
    try:
        rev_range = f"{git('describe', '--tags', '--abbrev=0')}..HEAD"
    except subprocess.CalledProcessError:
        rev_range = "HEAD"
    return [
        line
        for line in git("log", rev_range, "--format=%s%n%b").splitlines()
        if line.strip()
    ]


def detect_bump(messages: list[str]) -> str:
    if any(BREAKING_RE.match(m) or m.startswith("BREAKING CHANGE") for m in messages):
        return "major"
    if any(m.startswith("feat") for m in messages):
        return "minor"
    return "patch"


def next_version(version: str, bump: str) -> str:
    major, minor, patch = (int(part) for part in version.split("."))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def bump_pyproject(new_version: str) -> None:
    PYPROJECT.write_text(
        VERSION_RE.sub(f'version = "{new_version}"', PYPROJECT.read_text(), count=1)
    )


def refresh_lock() -> None:
    if (ROOT / "uv.lock").exists():
        subprocess.run(["uv", "lock"], cwd=ROOT, check=True)


def update_changelog(new_version: str) -> None:
    subprocess.run(
        [
            "git-cliff",
            "--unreleased",
            "--tag",
            new_version,
            "--prepend",
            str(CHANGELOG),
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--type",
        choices=BUMP_TYPES,
        default=None,
        help="version bump to apply (default: auto-detect from commits since the last tag)",
    )
    args = parser.parse_args()

    if git("status", "--porcelain"):
        raise SystemExit(
            "working tree is not clean; commit or stash your changes first"
        )

    bump = args.type or detect_bump(messages_since_last_tag())
    new_version = next_version(current_version(), bump)
    bump_pyproject(new_version)
    update_changelog(new_version)
    refresh_lock()
    git("add", "pyproject.toml", "CHANGELOG.md", "uv.lock")
    git("commit", "-m", f"chore(release): {new_version}")
    git("tag", new_version)
    print(
        f"Released {new_version} ({bump}). Push with: git push && git push origin {new_version}"
    )
