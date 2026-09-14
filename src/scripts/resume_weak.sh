#!/usr/bin/env bash
# continua a escalabilidade fraca a partir do weak.csv atual, sem apagar
# as linhas ja medidas. usa a mesma regra spp = SPP_BASE * p e as mesmas
# 10 repeticoes. so dispara as combinacoes (threads, spp) que ainda nao
# tem REPS amostras.
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

if [[ ! -f "$OUT" ]]; then
    echo "version,label,threads,schedule,w,h,spp,time_s,time_par_s,checksum" > "$OUT"
fi

count_rows() {
    local t="$1"
    awk -F',' -v t="$t" 'NR>1 && $3==t { n++ } END { print n+0 }' "$OUT"
}

need_seq=$(count_rows 1)
echo "seq ja tem $need_seq / $REPS"
if [[ "$need_seq" -lt "$REPS" ]]; then
    for r in $(seq $((need_seq + 1)) "$REPS"); do
        echo ">>> seq rep $r"
        "$BIN_SEQ" -w "$W" -h "$H" -s "$SPP_BASE" --label seq 2>/dev/null | tail -1 >> "$OUT"
    done
fi

for t in 2 4 6 8 10 12; do
    spp=$((SPP_BASE * t))
    have=$(count_rows "$t")
    echo "t=$t spp=$spp ja tem $have / $REPS"
    if [[ "$have" -ge "$REPS" ]]; then
        continue
    fi
    for r in $(seq $((have + 1)) "$REPS"); do
        echo ">>> omp t=$t rep $r"
        OMP_NUM_THREADS="$t" "$BIN_OMP" -w "$W" -h "$H" -s "$spp" \
            --schedule "dynamic,4" --label "omp_t${t}" 2>/dev/null | tail -1 >> "$OUT"
    done
done

echo
echo "--- $OUT ---"
column -s, -t "$OUT" | tail -20
