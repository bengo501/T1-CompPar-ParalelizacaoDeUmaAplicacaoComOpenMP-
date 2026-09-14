#!/usr/bin/env bash
# resume o desbalanceamento por politica: min, media, max e imbalance
# (max-min). imbalance alto significa que as ultimas threads chegam
# muito depois das primeiras, deixando cores ociosos.
set -eu
cd "$(dirname "$0")/.."

f=results/balance.csv
[[ -f "$f" ]] || { echo "rode scripts/run_sched.sh antes" >&2; exit 1; }

echo "--- primeiras linhas do balance.csv ---"
head -20 "$f"
echo
echo "--- imbalance por politica ---"
awk -F',' '
  NR>1 {
    pol=$1; tm=$3+0;
    if (!(pol in mn) || tm<mn[pol]) mn[pol]=tm;
    if (tm>mx[pol]) mx[pol]=tm;
    sm[pol]+=tm; n[pol]++;
  }
  END {
    for (p in n) {
      m = sm[p]/n[p];
      printf "%-14s  min=%.3f  media=%.3f  max=%.3f  imbalance=%.3f  ineff=%.1f%%\n",
             p, mn[p], m, mx[p], mx[p]-mn[p], (mx[p]-m)/mx[p]*100;
    }
  }
' "$f" | sort
