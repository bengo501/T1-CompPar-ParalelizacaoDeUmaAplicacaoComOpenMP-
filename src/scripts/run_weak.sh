#!/usr/bin/env bash
# escalabilidade fraca: trabalho por thread constante.
# custo do smallpt e proporcional a w*h*spp; mantemos w e h fixos e
# escalamos spp linearmente com o numero de threads (regra: spp = spp_base * p).
# assim o trabalho total escala como p, e cada thread recebe sempre spp_base
# amostras por subpixel do bloco de linhas que lhe cabe.
#
# base spp = 32 (mesma entrada da escalabilidade forte).
set -eu
cd "$(dirname "$0")/.."

BIN_SEQ=./bin/smallpt_seq
BIN_OMP=./bin/smallpt_omp
[[ -x "$BIN_SEQ" && -x "$BIN_OMP" ]] || { echo "compile antes: make all" >&2; exit 1; }

W=${W:-800}
H=${H:-600}
# base = mesma entrada da escalabilidade forte (spp=32), como pede o
# enunciado corrigido. o trabalho por thread e mantido constante escalando
# spp linearmente com p, ja que o custo do renderer e O(w*h*spp).
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
        # politica escolhida por medicao: dynamic,4 (ver results/balanceamento.md).
        OMP_NUM_THREADS="$t" "$BIN_OMP" -w "$W" -h "$H" -s "$spp" \
            --schedule "dynamic,4" --label "omp_t${t}" 2>/dev/null | tail -1 >> "$OUT"
    done
done

echo
echo "--- $OUT ---"
column -s, -t "$OUT"
