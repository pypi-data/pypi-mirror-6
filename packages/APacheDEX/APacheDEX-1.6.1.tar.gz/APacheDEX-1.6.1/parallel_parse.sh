#!/bin/bash
usage() {
  echo "Usage:"
  echo "  find [...] -print0 | $0 \\"
  echo "    parallelism state_dir out_file command [arg1 [...]]"
  echo "Reads filenames to process from stdin, null-delimited."
  echo
  echo "Example: parsing any number of log files with up to 4"
  echo "processes in parallel with locally built pypy:"
  echo "  $ mkdir state"
  echo "  $ $0 4 state out.tml /usr/local/bin/pypy \\"
  echo "    bin/apachedex --period week"
}

if [ $# -lt 4 ]; then
  usage
  exit 1
fi

if [ "$1" = "-h" -o "$1" = "--help" ]; then
  usage
  exit 0
fi

PARALLELISM="$1"
shift
STATE_DIR="$1"
mkdir -p "$STATE_DIR" || exit $?
shift
OUT_FILE="$1"
shift

# XXX: any simpler way ?
xargs -0 -r -n 1 -P "$PARALLELISM" -I "@FILE@" -- "$SHELL" -c 'INFILE="$1";shift;STATE_DIR="$1";shift;echo -n .;exec "$@" -Q --format json --out "$STATE_DIR/$(sed s:/:@:g <<< "$INFILE").json" "$INFILE"' "$0" "@FILE@" "$STATE_DIR" "$@"
echo
# XXX: what if there are too many state files for a single execution ?
find "$STATE_DIR" -type f -print0 | xargs -0 -r "$@" --out "$OUT_FILE" --state-file
