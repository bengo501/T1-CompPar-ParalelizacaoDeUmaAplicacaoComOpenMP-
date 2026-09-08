#!/usr/bin/env bash
# imprime o log agregado e o estado dos csvs.
set -eu
cd "$(dirname "$0")/.."
cat results/run_all.log 2>/dev/null | tail -30
echo "---"
for f in sched strong weak; do
    if [[ -f "results/$f.csv" ]]; then
        n=$(wc -l < "results/$f.csv")
        echo "$f.csv: $n linhas"
    else
        echo "$f.csv: ainda nao existe"
    fi
done
