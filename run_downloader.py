import argparse
import glob
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

    pattern = f"/Workspace/Users/*/{folder_name}/utilities/downloader.sh"
    paths = glob.glob(pattern)

    if not paths:
        raise FileNotFoundError(
            f"No downloader.sh found for folder {folder_name}",
        )

    # If multiple paths match, pick the first one deterministically
    script_path = sorted(paths)[0]

    print(f"Executing {script_path}")

    subprocess.run(["bash", script_path], check=True)


if __name__ == "__main__":
    main()
