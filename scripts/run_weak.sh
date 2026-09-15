#!/usr/bin/env bash
# escalabilidade fraca: spp = 32 * p (custo O(w*h*spp)).
set -eu
cd "$(dirname "$0")/.."

BIN_SEQ=./bin/smallpt_seq
BIN_OMP=./bin/smallpt_omp
[[ -x "$BIN_SEQ" && -x "$BIN_OMP" ]] || { echo "compile antes: make all" >&2; exit 1; }

W=${W:-800}
H=${H:-600}
SPP_BASE=${SPP_BASE:-32}
REPS=${REPS:-10}

OUT=results/weak.csv
mkdir -p results
echo "version,label,threads,schedule,w,h,spp,time_s,time_par_s,checksum" > "$OUT"

echo "--- referencia sequencial (T1, spp=$SPP_BASE) ---"
for r in $(seq 1 "$REPS"); do
    echo ">>> seq rep $r"
    "$BIN_SEQ" -w "$W" -h "$H" -s "$SPP_BASE" --label seq | tail -1 >> "$OUT"
done

for t in 2 4 6 8 10 12; do
    spp=$((SPP_BASE * t))
    echo "--- paralelo com $t threads, spp=$spp ---"
    for r in $(seq 1 "$REPS"); do
        echo ">>> omp t=$t rep $r"
        OMP_NUM_THREADS="$t" "$BIN_OMP" -w "$W" -h "$H" -s "$spp" \
            --schedule "dynamic,4" --label "omp_t${t}" 2>/dev/null | tail -1 >> "$OUT"
    done
done

echo
echo "--- $OUT ---"
column -s, -t "$OUT"
