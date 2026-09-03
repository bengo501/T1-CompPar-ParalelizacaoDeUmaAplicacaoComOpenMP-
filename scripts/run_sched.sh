#!/usr/bin/env bash
# compara politicas de escalonamento em 12 threads e imprime a distribuicao
# de carga por thread para cada uma. gera:
#   results/sched.csv       linhas csv com tempo por politica (3 repeticoes)
#   results/balance.csv     tempo e iteracoes por thread por politica (1 amostra)
set -eu
cd "$(dirname "$0")/.."

BIN=./bin/smallpt_omp
[[ -x "$BIN" ]] || { echo "compile antes: make omp" >&2; exit 1; }

W=${W:-800}
H=${H:-600}
SPP=${SPP:-32}
THREADS=${THREADS:-12}
REPS=${REPS:-3}

OUT_TIMES=results/sched.csv
OUT_BAL=results/balance.csv
mkdir -p results
echo "version,label,threads,schedule,w,h,spp,time_s,checksum" > "$OUT_TIMES"
echo "schedule,thread,time_s,iters" > "$OUT_BAL"

policies=("static" "static,32" "static,4" "dynamic" "dynamic,32" "dynamic,4" "guided")

for pol in "${policies[@]}"; do
    label="sched_${pol//,/_}"
    for r in $(seq 1 "$REPS"); do
        echo ">>> $pol rep $r"
        OMP_NUM_THREADS="$THREADS" "$BIN" -w "$W" -h "$H" -s "$SPP" \
            --schedule "$pol" --label "$label" \
            2>/dev/null | tail -1 >> "$OUT_TIMES"
    done
    # uma amostra extra com balance profiling. pol vai com underscore no
    # csv para nao colidir com o proprio separador (evita "static,32").
    pol_id="${pol//,/_}"
    OMP_NUM_THREADS="$THREADS" "$BIN" -w "$W" -h "$H" -s "$SPP" \
        --schedule "$pol" --label "${label}_bal" --profile-balance \
        > /dev/null 2> results/_bal_tmp.csv
    awk -v pol="$pol_id" -F',' '
      /^balance,/ { printf "%s,%s,%s,%s\n", pol, $2, $3, $4 }
    ' results/_bal_tmp.csv >> "$OUT_BAL"
done
rm -f results/_bal_tmp.csv

echo "--- $OUT_TIMES ---"
column -s, -t "$OUT_TIMES"
echo
echo "--- resumo de balanceamento (mediana min max por politica) ---"
awk -F',' 'NR>1 { key=$1; t[key,++n[key]]=$3 }
END {
  for (k in n) {
    m = n[k]; nsplit = 0;
    for (i=1;i<=m;i++) v[i]=t[k,i]+0;
    # ordenar
    for (i=1;i<=m;i++) for (j=i+1;j<=m;j++) if (v[i]>v[j]) { s=v[i]; v[i]=v[j]; v[j]=s }
    med = (m%2)?v[(m+1)/2]:(v[m/2]+v[m/2+1])/2;
    printf "%-14s min=%.3f  med=%.3f  max=%.3f  span=%.3f\n", k, v[1], med, v[m], v[m]-v[1];
  }
}' "$OUT_BAL" | sort
