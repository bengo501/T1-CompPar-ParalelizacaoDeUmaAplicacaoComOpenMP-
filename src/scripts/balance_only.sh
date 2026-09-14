#!/usr/bin/env bash
# so as amostras de balanceamento (uma por politica), para o caso em que
# os tempos ja foram medidos e o csv de balance precisou ser regerado.
set -eu
cd "$(dirname "$0")/.."

BIN=./bin/smallpt_omp
W=${W:-800} H=${H:-600} SPP=${SPP:-32} THREADS=${THREADS:-12}
OUT_BAL=results/balance.csv
mkdir -p results
echo "schedule,thread,time_s,iters" > "$OUT_BAL"

for pol in "static" "static,32" "static,4" "dynamic" "dynamic,32" "dynamic,4" "guided"; do
    pol_id="${pol//,/_}"
    echo ">>> $pol"
    OMP_NUM_THREADS="$THREADS" "$BIN" -w "$W" -h "$H" -s "$SPP" \
        --schedule "$pol" --label "bal_${pol_id}" --profile-balance \
        > /dev/null 2> results/_bal_tmp.csv
    awk -v pol="$pol_id" -F',' '/^balance,/ { printf "%s,%s,%s,%s\n", pol, $2, $3, $4 }' \
        results/_bal_tmp.csv >> "$OUT_BAL"
done
rm -f results/_bal_tmp.csv
echo done
