#!/usr/bin/env bash
# escalabilidade forte: tamanho fixo, threads crescente na serie
# 1, 2, 4, 6, 8, 10, 12 (12 = num de threads logicas do ryzen 5 3600).
# 10 repeticoes por ponto. o ponto de 1 thread e o binario sequencial
# (compilado sem -fopenmp), nao o omp com OMP_NUM_THREADS=1.
set -eu
cd "$(dirname "$0")/.."

BIN_SEQ=./bin/smallpt_seq
BIN_OMP=./bin/smallpt_omp
[[ -x "$BIN_SEQ" && -x "$BIN_OMP" ]] || { echo "compile antes: make all" >&2; exit 1; }

W=${W:-800}
H=${H:-600}
SPP=${SPP:-32}
REPS=${REPS:-10}

OUT=results/strong.csv
mkdir -p results
echo "version,label,threads,schedule,w,h,spp,time_s,time_par_s,checksum" > "$OUT"

echo "--- referencia sequencial (T1) ---"
for r in $(seq 1 "$REPS"); do
    echo ">>> seq rep $r"
    "$BIN_SEQ" -w "$W" -h "$H" -s "$SPP" --label seq | tail -1 >> "$OUT"
done

for t in 2 4 6 8 10 12; do
    echo "--- paralelo com $t threads ---"
    for r in $(seq 1 "$REPS"); do
        echo ">>> omp t=$t rep $r"
        # politica escolhida por medicao: dynamic,4 (ver results/balanceamento.md).
        OMP_NUM_THREADS="$t" "$BIN_OMP" -w "$W" -h "$H" -s "$SPP" \
            --schedule "dynamic,4" --label "omp_t${t}" 2>/dev/null | tail -1 >> "$OUT"
    done
done

echo
echo "--- $OUT ---"
column -s, -t "$OUT"
