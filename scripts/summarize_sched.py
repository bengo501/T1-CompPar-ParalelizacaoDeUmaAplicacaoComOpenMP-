"""imprime mediana, min e max por politica em results/sched.csv."""
import csv, statistics, sys, pathlib
p = pathlib.Path(__file__).resolve().parent.parent / "results" / "sched.csv"
d = {}
for r in csv.DictReader(open(p)):
    d.setdefault(r["label"], []).append(float(r["time_s"]))
for k in sorted(d):
    v = d[k]
    print(f"{k:22s} med={statistics.median(v):.3f} min={min(v):.3f} max={max(v):.3f}")
