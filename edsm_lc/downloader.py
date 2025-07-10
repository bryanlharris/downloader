#!/usr/bin/env python3
"""Downloader utility implemented in Python.

This variant targets the ``edsm_lc`` catalog and ``edsm_bronze`` schema in
Unity Catalog.  It mirrors the behaviour of ``downloader.sh`` but writes
temporary files only under ``/tmp``.  After processing, the data is copied to
the UC destination and all temporary files are removed.  A marker directory is
created for each timestamped download so that subsequent executions skip files
that were already processed.
"""
from __future__ import annotations

import argparse
import gzip
import os
import shutil
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path


def stream_gz_to_ndjson(gz_path: Path, ndjson_path: Path) -> None:
    """Convert a gzipped JSON array file to NDJSON.

    The original EDSM dumps are ``[ {...}, {...}, ... ]``.  This function
    removes the enclosing array brackets and trailing commas so that each
    object is written on its own line as valid JSON.
    """
    with gzip.open(gz_path, 'rt', encoding='utf-8') as src, ndjson_path.open('w', encoding='utf-8') as dst:
        first = True
        for line in src:
            line = line.strip()
            if first:
                # Remove opening '[' if present
                if line.startswith('['):
                    line = line[1:]
                first = False
            # Remove closing ']' if present
            if line.endswith(']'):
                line = line[:-1]
            # Trim trailing comma
            if line.endswith(','):
                line = line[:-1]
            line = line.strip()
            if line:
                dst.write(line + '\n')


def download(timestamp_check: str, urls: list[str], root: Path, marker_root: Path) -> None:
    """Download and process the given URLs if the marker does not exist."""
    date_str = datetime.now().strftime('%Y%m%d')
    with tempfile.TemporaryDirectory(dir='/tmp') as tmp_dir:
        tmp_base = Path(tmp_dir)
        tmp_save_dir = tmp_base / date_str
        root_save_dir = root / date_str
        check_dir = marker_root / timestamp_check

        if check_dir.exists():
            # Already downloaded
            return

        tmp_save_dir.mkdir(parents=True, exist_ok=True)
        root_save_dir.mkdir(parents=True, exist_ok=True)
        check_dir.mkdir(parents=True, exist_ok=True)
        (check_dir / 'marker').touch()

        for url in urls:
            filename = os.path.basename(url)
            if filename.endswith('.gz'):
                filename = filename[:-3]

            gz_path = tmp_save_dir / f"{filename}.gz"
            ndjson_tmp = tmp_save_dir / filename
            dest_file = root_save_dir / filename

            with urllib.request.urlopen(url) as response, gz_path.open('wb') as out:
                shutil.copyfileobj(response, out)

            stream_gz_to_ndjson(gz_path, ndjson_tmp)
            gz_path.unlink()  # remove gz file

            shutil.copy2(ndjson_tmp, dest_file)
            ndjson_tmp.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Python downloader")
    parser.add_argument(
        '--root',
        default='/Volumes/dev_lc/edsm_bronze/landing/data',
        help='Destination root path (UC path)'
    )
    parser.add_argument(
        '--marker-root',
        default='/Volumes/dev_lc/edsm_bronze/landing/markers',
        help='Marker directory root'
    )
    args = parser.parse_args()

    root = Path(args.root)
    marker_root = Path(args.marker_root)
    root.mkdir(parents=True, exist_ok=True)
    marker_root.mkdir(parents=True, exist_ok=True)
    (marker_root / 'marker').touch(exist_ok=True)

    # Yearly example
    download(datetime.now().strftime('%Y'),
             ['https://www.edsm.net/dump/systemsWithCoordinates.json.gz'],
             root, marker_root)

    # Weekly example
    download(f"{datetime.now().strftime('%Y')}_week{datetime.now().strftime('%U')}",
             [
                 'https://www.edsm.net/dump/stations.json.gz',
                 'https://www.edsm.net/dump/codex.json.gz',
             ],
             root, marker_root)

    # Daily example
    download(datetime.now().strftime('%Y%m%d'),
             [
                 'https://www.edsm.net/dump/powerPlay.json.gz',
                 'https://www.edsm.net/dump/systemsPopulated.json.gz',
                 'https://www.edsm.net/dump/bodies7days.json.gz',
                 'https://www.edsm.net/dump/systemsWithCoordinates7days.json.gz',
                 'https://www.edsm.net/dump/systemsWithoutCoordinates.json.gz',
             ],
             root, marker_root)


if __name__ == '__main__':
    main()
