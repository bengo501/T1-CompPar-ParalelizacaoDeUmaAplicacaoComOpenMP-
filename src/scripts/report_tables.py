"""imprime, no formato exato do relatorio em latex, as tabelas 1, 2 e 3.

le results/strong.csv, results/weak.csv e results/sched.csv, calcula
mediana, min e max por configuracao com 10 repeticoes e emite tres blocos
de texto prontos para colar no .tex.

uso:
    python scripts/report_tables.py
"""
import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def group(path, key):
    d = {}
    if not path.exists():
        return d
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            k = key(row)
            d.setdefault(k, []).append(float(row["time_s"]))
    return d


def fmt(x):
    return f"{x:.3f}".replace(".", "{,}")


def strong_table():
    g = group(RESULTS / "strong.csv", lambda r: int(r["threads"]))
    xs = sorted(g)
    t1_med = statistics.median(g[1])
    print("% tabela 1: escalabilidade forte")
    print(r"\begin{tabular}{r r r r r r}")
    print(r"  \toprule")
    print(r"  Threads & Mediana (s) & Min (s) & Max (s) & Speed-up & Eficiencia \\")
    print(r"  \midrule")
    for p in xs:
        v = g[p]
        med, mn, mx = statistics.median(v), min(v), max(v)
        sp = t1_med / med
        ef = sp / p * 100
        rot = "seq, $T_1$" if p == 1 else f"{p}"
        first = f"{rot} " if p == 1 else f"{p}"
        print(f"  {first} & {fmt(med)} & {fmt(mn)} & {fmt(mx)} & "
              f"{fmt(sp)} & {ef:.1f}\\% \\\\")
    print(r"  \bottomrule")
    print(r"\end{tabular}")
    return g, t1_med


def weak_table():
    g = {}
    if not (RESULTS / "weak.csv").exists():
        print("% weak.csv nao existe ainda")
        return
    with (RESULTS / "weak.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            p = int(row["threads"])
            g.setdefault(p, {"spp": int(row["spp"]), "t": []})
            g[p]["t"].append(float(row["time_s"]))
    xs = sorted(g)
    t1_med = statistics.median(g[1]["t"])
    print()
    print("% tabela 2: escalabilidade fraca")
    print(r"\begin{tabular}{r r r r r r}")
    print(r"  \toprule")
    print(r"  Threads & spp & Mediana (s) & Min (s) & Max (s) & Eficiencia \\")
    print(r"  \midrule")
    for p in xs:
        v = g[p]["t"]
        med, mn, mx = statistics.median(v), min(v), max(v)
        ef = t1_med / med * 100
        spp = g[p]["spp"]
        rot = "seq, $T_1$" if p == 1 else f"{p}"
        print(f"  {rot} & {spp} & {fmt(med)} & {fmt(mn)} & {fmt(mx)} & {ef:.1f}\\% \\\\")
    print(r"  \bottomrule")
    print(r"\end{tabular}")


def sched_table():
    if not (RESULTS / "sched.csv").exists():
        print("% sched.csv nao existe ainda")
        return
    g = {}
    with (RESULTS / "sched.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            k = row["schedule"]
            g.setdefault(k, []).append(float(row["time_s"]))
    order = ["static", "static_32", "static_4", "dynamic", "dynamic_32",
             "dynamic_4", "guided"]
    pretty = {"static": "static", "static_32": "static, 32",
              "static_4": "static, 4", "dynamic": "dynamic",
              "dynamic_32": "dynamic, 32", "dynamic_4": "dynamic, 4 (adotada)",
              "guided": "guided"}
    print()
    print("% tabela 3: politicas de scheduling em 12 threads")
    print(r"\begin{tabular}{l r r r}")
    print(r"  \toprule")
    print(r"  Politica & Mediana (s) & Min (s) & Max (s) \\")
    print(r"  \midrule")
    for k in order:
        if k not in g:
            continue
        v = g[k]
        med, mn, mx = statistics.median(v), min(v), max(v)
        print(f"  {pretty[k]} & {fmt(med)} & {fmt(mn)} & {fmt(mx)} \\\\")
    print(r"  \bottomrule")
    print(r"\end{tabular}")


if __name__ == "__main__":
    strong_table()
    weak_table()
    sched_table()
