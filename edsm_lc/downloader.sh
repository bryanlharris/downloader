#!/usr/bin/bash

# Create a temporary directory
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

root="/Volumes/dev_lc/edsm_bronze/landing/data"
marker_root="/Volumes/dev_lc/edsm_bronze/landing/markers"

install -dv "$root" "$marker_root"
touch "$marker_root/marker"

# Download function
download(){
    ts_check="$1"
    shift
    tmp_save_dir="$tmp_dir/$(date +%Y%m%d)"
    root_save_dir="$root/$(date +%Y%m%d)"
    check_dir="$marker_root/$ts_check"
    if [[ ! -d "$check_dir" ]]; then
        install -dv "$tmp_save_dir" "$root_save_dir" "$check_dir"
        touch "$check_dir/marker"
        (
            cd "$tmp_save_dir"
            for url in "$@"; do
                filename=$(basename "$url" .gz)
                wget -nv -O - "$url" \
                    | gunzip -c \
                    | sed \
                        -e '1s/^\[//' \
                        -e '$s/]$//' \
                        -e 's/^[[:space:]]*//' \
                        -e 's/},$/}/' > "$filename"
                cat "$tmp_save_dir/$filename" > "$root_save_dir/$filename"
                rm "$tmp_save_dir/$filename"
            done
        )
    fi
}

# yearly example
download "$(date +%Y)" https://www.edsm.net/dump/systemsWithCoordinates.json.gz

# Weekly example
download "$(date +%Y)_week$(date +%U)" https://www.edsm.net/dump/stations.json.gz \
    https://www.edsm.net/dump/codex.json.gz

# daily
download "$(date +%Y%m%d)" https://www.edsm.net/dump/powerPlay.json.gz \
    https://www.edsm.net/dump/systemsPopulated.json.gz \
    https://www.edsm.net/dump/bodies7days.json.gz \
    https://www.edsm.net/dump/systemsWithCoordinates7days.json.gz \
    https://www.edsm.net/dump/systemsWithoutCoordinates.json.gz

