#!/usr/bin/env bash
# roda so as duas escalabilidades (sched ja foi feito).
set -eu
cd "$(dirname "$0")/.."

date -Iseconds
echo "=== 3/4 strong (7 pontos x 10 reps) ==="; bash scripts/run_strong.sh > /tmp/strong.log 2>&1 && echo "strong ok"
date -Iseconds
echo "=== 4/4 weak (7 pontos x 10 reps, base spp=32) ==="; bash scripts/run_weak.sh > /tmp/weak.log 2>&1 && echo "weak ok"
date -Iseconds
echo "=== tudo pronto ==="
