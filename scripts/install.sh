#!/bin/sh
set -eu

usage() {
    cat <<'EOF'
Usage: install.sh --profile standard|fusion [--dry-run]

Installs XR-AUD packages from APT sources already configured by the operator.
This script never adds a repository, imports a key, or embeds credentials.
EOF
}

profile=""
dry_run=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --profile)
            [ "$#" -ge 2 ] || { usage >&2; exit 2; }
            profile=$2
            shift 2
            ;;
        --dry-run)
            dry_run=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage >&2
            exit 2
            ;;
    esac
done

case "$profile" in
    standard)
        packages="xraudio-audio-defaults"
        ;;
    fusion)
        packages="xraudio-audio-defaults libxraudio0 xraudio-runtime xraudio-ros2-bridge"
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac

if [ "$dry_run" -eq 1 ]; then
    # Intentional word splitting: packages is a fixed internal list selected above.
    apt-get -s install $packages
    exit 0
fi

if [ "$(id -u)" -ne 0 ]; then
    echo "Run as root after reviewing the selected packages." >&2
    exit 1
fi

# Intentional word splitting: packages is a fixed internal list selected above.
apt-get install $packages
