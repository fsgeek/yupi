#!/usr/bin/env bash
# Full two-path gate for a window law, sharded: for each (rung, eps) in order,
# launch N interleaved shards of scripts/window_gate.py, wait for them, go on.
# Each shard rebuilds the recursion and gates windows i, i+N, ... in support
# order; a (rung, eps) is gated iff every shard reports zero mismatches and the
# shard counts sum to the recursion's window total (checked by the reader, not
# here). PIDs are recorded in $OUT/pids and killed by PID only; every shard runs
# under ulimit -v (KB). Usage:
#   scripts/window_gate_driver.sh T_ep L B OUTDIR [N=8] [ULIMIT_KB=20000000]
# with YUPI_PROGRAMS set; the (rung, eps) order is r4 1, r4 1/2, r1, r2, r3, r0.
set -u
T_ep=$1; L=$2; B=$3; OUT=$4; N=${5:-8}; UL=${6:-20000000}
mkdir -p "$OUT"
echo "driver start $(date) law=($T_ep,$L,$B) N=$N programs=${YUPI_PROGRAMS:-c1}" >> "$OUT/driver.log"
for job in "r4 1" "r4 1/2" "r1 1" "r1 1/2" "r2 1" "r2 1/2" "r3 1" "r3 1/2" "r0 1" "r0 1/2"; do
  set -- $job; rung=$1; eps=$2; tag="${rung}-eps$(echo "$eps" | tr '/' '_')"
  echo "$(date) launching $tag ($N shards)" >> "$OUT/driver.log"
  pids=()
  for i in $(seq 0 $((N-1))); do
    ( ulimit -v "$UL"; YUPI_EPS="$eps" uv run python scripts/window_gate.py "$T_ep" "$L" "$B" "$rung" --shard "$i/$N" "$OUT/gate-$tag-shard$i.json" > "$OUT/gate-$tag-shard$i.log" 2>&1 ) &
    pids+=($!)
  done
  printf '%s\n' "${pids[@]}" >> "$OUT/pids"
  for p in "${pids[@]}"; do wait "$p"; echo "$(date) $tag pid $p exit $?" >> "$OUT/driver.log"; done
done
echo "driver end $(date)" >> "$OUT/driver.log"
