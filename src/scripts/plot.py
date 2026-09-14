"""gera os graficos do t1: speed-up e eficiencia para as escalabilidades
forte e fraca. le results/strong.csv e results/weak.csv, calcula mediana
por numero de threads, e produz results/speedup.pdf e results/efficiency.pdf.

uso:
    python scripts/plot.py

os pdfs sao usados no relatorio em latex."""
import csv
import os
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

PHYSICAL_CORES = 6
LOGICAL_CORES = 12


def read_csv(path):
    """agrupa tempos por (threads,) e devolve dict {threads: [tempos]}."""
    d = {}
    if not path.exists():
        return d
    with path.open(newline="") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            t = int(row["threads"])
            tm = float(row["time_s"])
            d.setdefault(t, []).append(tm)
    return d


def median_series(times_dict):
    xs = sorted(times_dict.keys())
    ys = [statistics.median(times_dict[x]) for x in xs]
    mn = [min(times_dict[x]) for x in xs]
    mx = [max(times_dict[x]) for x in xs]
    return xs, ys, mn, mx


def strong_metrics(strong):
    xs, medians, mn, mx = median_series(strong)
    t1 = medians[xs.index(1)]
    speedups = [t1 / t for t in medians]
    effs = [s / p * 100 for s, p in zip(speedups, xs)]
    return xs, medians, speedups, effs, mn, mx


def weak_metrics(weak):
    xs, medians, mn, mx = median_series(weak)
    t1 = medians[xs.index(1)]
    effs = [t1 / t * 100 for t in medians]
    return xs, medians, effs


def annotate_smt(ax):
    ax.axvline(PHYSICAL_CORES, color="0.4", linestyle=":", linewidth=1)
    ymin, ymax = ax.get_ylim()
    ax.text(PHYSICAL_CORES + 0.15, ymin + (ymax - ymin) * 0.05,
            "SMT (>6 threads)", color="0.3", fontsize=8, rotation=90,
            verticalalignment="bottom")


def main():
    strong = read_csv(RESULTS / "strong.csv")
    weak   = read_csv(RESULTS / "weak.csv")
    if not strong or not weak:
        raise SystemExit("faltam results/strong.csv ou results/weak.csv; "
                         "rode scripts/run_strong.sh e scripts/run_weak.sh")

    xs, tps, sps, effs, mn, mx = strong_metrics(strong)
    xw, tw, effw = weak_metrics(weak)

    print("--- escala forte ---")
    print("p\tt[s]\tsp\tef%")
    for p, t, s, e in zip(xs, tps, sps, effs):
        print(f"{p}\t{t:.3f}\t{s:.3f}\t{e:.1f}")
    print("--- escala fraca ---")
    print("p\tt[s]\tef%")
    for p, t, e in zip(xw, tw, effw):
        print(f"{p}\t{t:.3f}\t{e:.1f}")

    fig1, ax1 = plt.subplots(figsize=(5.2, 3.2))
    ideal = [p for p in xs]
    ax1.plot(xs, ideal, "--", color="0.5", label="ideal (y = p)")
    ax1.plot(xs, sps, "o-", color="C0", label="medido (mediana)")
    ax1.fill_between(xs,
                     [tps[0] / m for m in mx],
                     [tps[0] / m for m in mn],
                     color="C0", alpha=0.15, label="min/max")
    ax1.set_xlabel("numero de threads")
    ax1.set_ylabel("speed-up")
    ax1.set_title("escalabilidade forte  (w=800, h=600, spp=32)")
    ax1.set_xticks(xs)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left", fontsize=8)
    annotate_smt(ax1)
    fig1.tight_layout()
    p1 = RESULTS / "speedup.pdf"
    fig1.savefig(p1)
    print(f"escrito {p1}")

    fig2, ax2 = plt.subplots(figsize=(5.2, 3.2))
    ax2.plot(xs, effs, "o-", color="C0", label="forte  (T1/(p*Tp))")
    ax2.plot(xw, effw, "s-", color="C1", label="fraca  (T1/Tp)")
    ax2.axhline(100, color="0.5", linestyle="--", linewidth=1)
    ax2.set_xlabel("numero de threads")
    ax2.set_ylabel("eficiencia (%)")
    ax2.set_title("eficiencia: forte vs fraca")
    ax2.set_xticks(xs)
    ax2.set_ylim(0, 110)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="lower left", fontsize=8)
    annotate_smt(ax2)
    fig2.tight_layout()
    p2 = RESULTS / "efficiency.pdf"
    fig2.savefig(p2)
    print(f"escrito {p2}")

    # tambem em png para pre-visualizacao rapida
    fig1.savefig(RESULTS / "speedup.png", dpi=150)
    fig2.savefig(RESULTS / "efficiency.png", dpi=150)


if __name__ == "__main__":
    main()
