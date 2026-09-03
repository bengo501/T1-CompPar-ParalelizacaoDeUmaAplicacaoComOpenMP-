#!/usr/bin/env bash
# roda uma varredura de tamanhos para achar aquele em que o binario
# sequencial fica entre ~40 e 60 segundos.
set -eu
cd "$(dirname "$0")/.."

BIN=./bin/smallpt_seq
[[ -x "$BIN" ]] || { echo "compile antes: make seq" >&2; exit 1; }

configs=(
  "320 240 16"
  "480 360 16"
  "640 480 16"
  "640 480 32"
  "800 600 32"
)

for cfg in "${configs[@]}"; do
    read w h s <<< "$cfg"
    printf 'w=%s h=%s spp=%s ... ' "$w" "$h" "$s"
    "$BIN" -w "$w" -h "$h" -s "$s" --label calib | tail -1
done
