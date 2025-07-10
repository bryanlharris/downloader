import argparse
import os
import subprocess


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

    script_path = os.path.join(os.path.dirname(__file__), folder_name,
                               "utilities", "downloader.sh")

    if not os.path.isfile(script_path):
        raise FileNotFoundError(
            f"No downloader.sh found for folder {folder_name}",
        )

    print(f"Executing {script_path}")

    subprocess.run(["bash", script_path], check=True)


if __name__ == "__main__":
    main()
