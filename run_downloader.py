import argparse
import glob
import subprocess
from pathlib import Path


def main() -> None:
    """Locate and execute the matching downloader script."""
    parser = argparse.ArgumentParser(
        description="Run downloader script from workspace",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Folder name returned from list_download_scripts notebook",
    )
    args = parser.parse_args()
    folder_name = args.input

    pattern = str(Path.cwd() / "**" / "downloader.sh")
    candidates = [Path(p) for p in glob.glob(pattern, recursive=True)]
    matches = [p for p in candidates if p.parent.name == folder_name]

    if not matches:
        raise FileNotFoundError(
            f"No downloader.sh found for folder {folder_name}",
        )

    script_path = str(matches[0])

    print(f"Executing {script_path}")

    subprocess.run(["bash", script_path], check=True)


if __name__ == "__main__":
    main()
