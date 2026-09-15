"""gera results/speedup.pdf e results/efficiency.pdf a partir dos csvs."""
import csv
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
PHYSICAL_CORES = 6


def read_csv(path):
    d = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            t = int(row["threads"])
            d.setdefault(t, []).append(float(row["time_s"]))
    return d


def median_series(times_dict):
    xs = sorted(times_dict.keys())
    ys = [statistics.median(times_dict[x]) for x in xs]
    mn = [min(times_dict[x]) for x in xs]
    mx = [max(times_dict[x]) for x in xs]
    return xs, ys, mn, mx


def annotate_smt(ax):
    ax.axvline(PHYSICAL_CORES, color="0.4", linestyle=":", linewidth=1)
    ymin, ymax = ax.get_ylim()
    ax.text(PHYSICAL_CORES + 0.15, ymin + (ymax - ymin) * 0.05,
            "SMT (>6 threads)", color="0.3", fontsize=8, rotation=90,
            verticalalignment="bottom")


def main():
    strong = read_csv(RESULTS / "strong.csv")
    weak = read_csv(RESULTS / "weak.csv")
    xs, tps, mn, mx = median_series(strong)
    t1 = tps[xs.index(1)]
    sps = [t1 / t for t in tps]
    effs = [s / p * 100 for s, p in zip(sps, xs)]
    xw, tw, _, _ = median_series(weak)
    t1w = tw[xw.index(1)]
    effw = [t1w / t * 100 for t in tw]

    fig1, ax1 = plt.subplots(figsize=(5.2, 3.2))
    ax1.plot(xs, xs, "--", color="0.5", label="ideal (y = p)")
    ax1.plot(xs, sps, "o-", color="C0", label="medido (mediana)")
    ax1.fill_between(xs, [t1 / m for m in mx], [t1 / m for m in mn],
                     color="C0", alpha=0.15, label="min/max")
    ax1.set_xlabel("numero de threads")
    ax1.set_ylabel("speed-up")
    ax1.set_title("escalabilidade forte  (w=800, h=600, spp=32)")
    ax1.set_xticks(xs)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left", fontsize=8)
    annotate_smt(ax1)
    fig1.tight_layout()
    fig1.savefig(RESULTS / "speedup.pdf")

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
    fig2.savefig(RESULTS / "efficiency.pdf")
    print("escrito results/speedup.pdf e results/efficiency.pdf")


if __name__ == "__main__":
    main()
