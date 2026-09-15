#!/usr/bin/env bash
# perfil, 7 politicas, escalabilidade forte e fraca (10 reps por ponto).
#   bash scripts/run_all.sh
set -eu
cd "$(dirname "$0")/.."

mkdir -p results

date -Iseconds
echo "=== 1/4 profile ==="; bash scripts/profile.sh
date -Iseconds
echo "=== 2/4 sched (7 politicas x 10 reps) ==="; bash scripts/run_sched.sh
date -Iseconds
echo "=== 3/4 strong (7 pontos x 10 reps) ==="; bash scripts/run_strong.sh
date -Iseconds
echo "=== 4/4 weak (7 pontos x 10 reps, base spp=32) ==="; bash scripts/run_weak.sh
date -Iseconds
echo "=== tudo pronto ==="
ls -la results/
