#!/usr/bin/env bash
# roda o binario -pg na mesma entrada de referencia do speed-up
# (w=800 h=600 spp=32) e gera results/gprof.txt e results/gprof_flat.csv.
# a fracao paralelizavel e a soma do tempo em radiance() e nas funcoes
# chamadas por ela: essencialmente tudo o que ocorre dentro do laco em y.
set -eu
cd "$(dirname "$0")/.."

make prof >/dev/null

# mesma fase e mesma entrada de referencia usadas no speed-up (secao 5).
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
echo
echo "--- resumo escrito em $OUT_DIR/gprof.txt e $OUT_DIR/gprof_flat.csv ---"

rm -f gmon.out
