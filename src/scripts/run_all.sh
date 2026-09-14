#!/usr/bin/env bash
# executa todas as baterias de medicao em sequencia com 10 reps por ponto,
# imprime marcas de tempo entre etapas e grava um log agregado em
# results/run_all.log. rode assim:
#   bash scripts/run_all.sh
# ou em background:
#   nohup bash scripts/run_all.sh > results/run_all.log 2>&1 &
set -eu
cd "$(dirname "$0")/.."

mkdir -p results
LOG=results/run_all.log

date -Iseconds
echo "=== 1/4 profile ==="; bash scripts/profile.sh > /tmp/prof.log 2>&1 && echo "profile ok"
date -Iseconds
echo "=== 2/4 sched (7 politicas x 10 reps) ==="; bash scripts/run_sched.sh > /tmp/sched.log 2>&1 && echo "sched ok"
date -Iseconds
echo "=== 3/4 strong (7 pontos x 10 reps) ==="; bash scripts/run_strong.sh > /tmp/strong.log 2>&1 && echo "strong ok"
date -Iseconds
echo "=== 4/4 weak (7 pontos x 10 reps, base spp=32) ==="; bash scripts/run_weak.sh > /tmp/weak.log 2>&1 && echo "weak ok"
date -Iseconds
echo "=== tudo pronto ==="
ls -la results/
