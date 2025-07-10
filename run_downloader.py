#!/usr/bin/env python

import argparse
import glob
import subprocess
from pathlib import Path


def main() -> None:
    """Locate and execute the matching downloader script."""
    parser = argparse.ArgumentParser(
        description="Run downloader script from workspace"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Folder name returned from list_download_scripts notebook"
    )
    parser.add_argument(
        "-n",
        required=False,
        action='store_true',
        help="Echo instead of execute script"
    )
    args = parser.parse_args()
    folder_name = args.input

    pattern = str(Path.cwd() / "*" / "downloader.sh")
    candidates = [Path(p) for p in glob.glob(pattern, recursive=False)]
    matches = [p for p in candidates if p.parent.name == folder_name]

    if not matches:
        raise FileNotFoundError(
            f"No downloader.sh found for folder {folder_name}",
        )

    script_path = str(matches[0])

    if args.n:
        print(f"Echoing script path.")
        subprocess.run(["echo", script_path], check=True)
    else:
        print(f"Executing {script_path}")
        subprocess.run(["bash", script_path], check=True)


if __name__ == "__main__":
    main()
