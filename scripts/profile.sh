#!/usr/bin/env bash
# gprof na mesma entrada do speed-up (w=800 h=600 spp=32).
set -eu
cd "$(dirname "$0")/.."

make prof >/dev/null

W=${W:-800}
H=${H:-600}
SPP=${SPP:-32}
OUT_DIR=results
mkdir -p "$OUT_DIR"

echo "rodando bin/smallpt_prof -w $W -h $H -s $SPP ..."
./bin/smallpt_prof -w "$W" -h "$H" -s "$SPP" --label prof > "$OUT_DIR/gprof_run.csv"

gprof -b bin/smallpt_prof gmon.out > "$OUT_DIR/gprof.txt"
awk '
  /^ *[0-9]+\.[0-9]+/ && NF>=7 {
    printf "%s,%s,%s,%s\n", $1, $2, $3, $NF;
  }
' "$OUT_DIR/gprof.txt" | head -20 > "$OUT_DIR/gprof_flat.csv"

echo "--- topo do flat profile ---"
head -25 "$OUT_DIR/gprof.txt"
rm -f gmon.out
