#!/usr/bin/env bash
set -euo pipefail

# All wallpaper decoding and settings generation happen without privileges.
# sudo is allowed to invoke ONLY the root-owned, no-argument sync helper.
if [[ $EUID -eq 0 ]]; then
    echo "Run this script as your normal user, not root." >&2
    exit 1
fi
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$script_dir/prepare-video.py"
exec sudo -n -- /usr/local/libexec/ii-sddm-theme-sync
