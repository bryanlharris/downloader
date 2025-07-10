#!/usr/bin/env python3
"""Run multiple EDSM download tasks defined in a JSON configuration file."""
from __future__ import annotations

import argparse
import gzip
import os
import shutil
import tempfile
import subprocess
import shlex
from datetime import datetime
from pathlib import Path
from typing import Iterable

import json


def download_task(task: dict, *, dry_run: bool = False) -> None:
    """Download the URLs for a single task if not already done.

    Parameters
    ----------
    task: dict
        Task dictionary from the JSON configuration.
    dry_run: bool, optional
        If True, just print what would be done without performing downloads.
    """
    ts = datetime.now().strftime(task["timestamp"])
    root = Path(task["root"])
    marker_root = Path(task["marker_root"])

    with tempfile.TemporaryDirectory(dir="/tmp") as tmp_dir:
        tmp_save_dir = Path(tmp_dir) / ts
        root_save_dir = root / ts
        check_dir = marker_root / ts

        if check_dir.exists():
            print(f"Skipping {task['name']} (marker exists)")
            return

        for p in [tmp_save_dir, root_save_dir, check_dir]:
            if not dry_run:
                p.mkdir(parents=True, exist_ok=True)
        if not dry_run:
            (check_dir / "marker").touch()

        for url in task["urls"]:
            filename = os.path.basename(url)
            if filename.endswith(".gz"):
                filename = filename[:-3]

            ndjson_tmp = tmp_save_dir / filename
            dest_file = root_save_dir / filename

            if dry_run:
                print(f"Would download {url} to {dest_file}")
                continue

            cmd = [
                "bash",
                "-c",
                (
                    "wget -nv -O - "
                    + shlex.quote(url)
                    + " | gunzip -c | sed "
                    "-e '1s/^[[]' "
                    "-e '$s/]$//' "
                    "-e 's/^[[:space:]]*//' "
                    "-e 's/},$//'"
                ),
            ]

            with ndjson_tmp.open('w', encoding='utf-8') as out:
                subprocess.run(cmd, stdout=out, stderr=sys.stderr, check=True)

            shutil.copy2(ndjson_tmp, dest_file)
            ndjson_tmp.unlink()


def run_tasks(tasks: Iterable[dict], *, dry_run: bool = False) -> None:
    for task in tasks:
        download_task(task, dry_run=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run EDSM download tasks")
    parser.add_argument(
        "config",
        nargs="?",
        default="download_tasks.json",
        help="JSON configuration file",
    )
    parser.add_argument(
        "tasks",
        nargs="*",
        help="Names of tasks to run (defaults to all)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Print actions without downloading",
    )
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    all_tasks = cfg.get("tasks", [])

    selected = [t for t in all_tasks if not args.tasks or t["name"] in args.tasks]
    if not selected:
        raise SystemExit("No matching tasks found")

    run_tasks(selected, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
