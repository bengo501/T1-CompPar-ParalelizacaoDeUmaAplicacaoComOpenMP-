#!/usr/bin/env bash
# sete politicas em 12 threads, 10 repeticoes. gera results/sched.csv.
set -eu
cd "$(dirname "$0")/.."

BIN=./bin/smallpt_omp
[[ -x "$BIN" ]] || { echo "compile antes: make omp" >&2; exit 1; }

W=${W:-800}
H=${H:-600}
SPP=${SPP:-32}
THREADS=${THREADS:-12}
REPS=${REPS:-10}

OUT_TIMES=results/sched.csv
mkdir -p results
echo "version,label,threads,schedule,w,h,spp,time_s,time_par_s,checksum" > "$OUT_TIMES"

policies=("static" "static,32" "static,4" "dynamic" "dynamic,32" "dynamic,4" "guided")

for pol in "${policies[@]}"; do
    label="sched_${pol//,/_}"
    for r in $(seq 1 "$REPS"); do
        echo ">>> $pol rep $r"
        OMP_NUM_THREADS="$THREADS" "$BIN" -w "$W" -h "$H" -s "$SPP" \
            --schedule "$pol" --label "$label" \
            2>/dev/null | tail -1 >> "$OUT_TIMES"
    done
done

echo "--- $OUT_TIMES ---"
column -s, -t "$OUT_TIMES"
