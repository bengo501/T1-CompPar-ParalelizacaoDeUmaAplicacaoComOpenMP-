"""imprime todas as amostras de cada politica de sched.csv, para inspecao
manual quando algum tempo parece fora da curva."""
import csv, pathlib, statistics
p = pathlib.Path(__file__).resolve().parent.parent / "results" / "sched.csv"
d = {}
for r in csv.DictReader(open(p)):
    d.setdefault(r["schedule"], []).append(float(r["time_s"]))
for k in sorted(d):
    v = sorted(d[k])
    print(f"{k:14s}  n={len(v):2d}  med={statistics.median(v):.3f}  "
          f"min={min(v):.3f}  max={max(v):.3f}")
    print("    " + " ".join(f"{x:.2f}" for x in v))
