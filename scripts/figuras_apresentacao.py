"""gera figuras 16:9 para os slides do t1 (cena, path tracing, paralelismo).

uso:
    python scripts/figuras_apresentacao.py

saida em apresentacao/figuras/*.png
"""
from __future__ import annotations

import csv
import statistics
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "apresentacao" / "figuras"
ASSETS = Path(
    r"C:\Users\joxto\.cursor\projects"
    r"\c-Users-joxto-Downloads-T1-CompPar-ParalelizacaoDeUmaAplicacaoComOpenMP"
    r"\assets"
)
RESULTS = ROOT / "results"

PHYSICAL_CORES = 6
INK = "#1c1c1c"
MUTED = "#5c5c5c"
ACCENT = "#2b6cb0"
RED = "#c45c5c"
BLUE = "#4a72b8"
GOLD = "#c9a227"
TEAL = "#2a9d8f"


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 13,
        "axes.titlesize": 18,
        "axes.titleweight": "medium",
        "axes.labelsize": 13,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": 160,
        "axes.edgecolor": "#dddddd",
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
    })


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    print(f"escrito {path}")
    return path


def read_ppm(path):
    tokens = Path(path).read_text().split()
    if tokens[0] != "P3":
        raise ValueError(f"ppm inesperado em {path}")
    w, h = int(tokens[1]), int(tokens[2])
    rgb = np.array([int(x) for x in tokens[4:]], dtype=np.uint8)
    return rgb.reshape(h, w, 3)


def load_img(path):
    return np.array(Image.open(path).convert("RGB"))


def copy_assets():
    mapping = {
        "cornell-box-cena.png": "01_cena_cornell_ilustracao.png",
        "path-tracing-raios.png": "03_path_tracing_ilustracao.png",
        "materiais-diff-spec-refr.png": "05_materiais_ilustracao.png",
        "paralelismo-linhas.png": "07_paralelismo_ilustracao.png",
    }
    for src, dst in mapping.items():
        s = ASSETS / src
        if s.exists():
            Image.open(s).convert("RGB").save(OUT / dst, "PNG")
            print(f"copiado {dst}")


def fig_cena_rotulada():
    img = load_img(ASSETS / "cornell-box-cena.png")
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.imshow(img)
    ax.set_axis_off()
    h, w = img.shape[:2]

    def ann(text, xy, xytext, color=INK):
        ax.annotate(
            text, xy=xy, xytext=xytext,
            xycoords="axes fraction", textcoords="axes fraction",
            fontsize=13, color=color, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=color, lw=1.4),
            bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="#dddddd", alpha=0.92),
        )

    ann("parede vermelha\n(diffusa)", (0.18, 0.55), (0.08, 0.78), RED)
    ann("parede azul\n(diffusa)", (0.82, 0.55), (0.92, 0.78), BLUE)
    ann("luz de area", (0.50, 0.78), (0.50, 0.96), GOLD)
    ann("esfera especular\n(espelho)", (0.38, 0.48), (0.22, 0.18), ACCENT)
    ann("esfera refrativa\n(vidro)", (0.62, 0.48), (0.80, 0.18), TEAL)
    ann("camera", (0.50, 0.08), (0.68, 0.06), INK)
    ax.set_title("cornell box do smallpt: 9 esferas (6 paredes + 2 objetos + 1 luz)")
    save(fig, "02_cena_cornell_rotulada.png")


def fig_path_rotulado():
    img = load_img(ASSETS / "path-tracing-raios.png")
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.imshow(img)
    ax.set_axis_off()

    def box(text, xy, color=INK):
        ax.text(
            xy[0], xy[1], text, transform=ax.transAxes,
            fontsize=13, color=color, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="#dddddd", alpha=0.94),
        )

    box("camera", (0.10, 0.22))
    box("plano da imagem\n(um pixel destacado)", (0.22, 0.88), ACCENT)
    box("raio primario", (0.38, 0.58), ACCENT)
    box("outras amostras\nmonte carlo", (0.42, 0.18), MUTED)
    box("esfera especular", (0.62, 0.28), ACCENT)
    box("parede diffusa", (0.88, 0.55), RED)
    box("luz", (0.78, 0.92), GOLD)
    ax.set_title("path tracing: o pixel acumula a luz ao longo de caminhos aleatorios")
    save(fig, "04_path_tracing_rotulado.png")


def fig_materiais_rotulado():
    img = load_img(ASSETS / "materiais-diff-spec-refr.png")
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_axes([0.02, 0.12, 0.96, 0.78])
    ax.imshow(img)
    ax.set_axis_off()
    fig.suptitle("tres materiais da cena: o ricochete muda o custo por pixel", fontsize=18, y=0.96)
    labels = [
        (0.18, "diff  —  paredes\nvarios raios aleatorios"),
        (0.50, "spec  —  espelho\num unico raio refletido"),
        (0.82, "refr  —  vidro\nreflexao + refracao"),
    ]
    for x, text in labels:
        fig.text(x, 0.06, text, ha="center", va="center", fontsize=13, color=INK)
    path = OUT / "06_materiais_rotulado.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print(f"escrito {path}")


def fig_render_real():
    img = read_ppm(OUT / "render_640x480_spp16.ppm")
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.imshow(img)
    ax.set_axis_off()
    ax.set_title("saida real do smallpt  ·  640×480  ·  spp=16  ·  4×16=64 amostras/pixel")
    save(fig, "08_render_real.png")
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.imshow(img)
    ax2.set_axis_off()
    fig2.savefig(OUT / "08_render_real_limpo.png", dpi=160, bbox_inches="tight", pad_inches=0)
    plt.close(fig2)
    print(f"escrito {OUT / '08_render_real_limpo.png'}")


def fig_spp_comparacao():
    files = [
        ("render_spp1.ppm", "spp = 1   ·   4 amostras/pixel   ·   ruido alto"),
        ("render_spp4.ppm", "spp = 4   ·   16 amostras/pixel"),
        ("render_spp16.ppm", "spp = 16   ·   64 amostras/pixel"),
        ("render_spp32.ppm", "spp = 32 (referencia)   ·   128 amostras/pixel"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(16, 9))
    for ax, (fname, title) in zip(axes.ravel(), files):
        ax.imshow(read_ppm(OUT / fname))
        ax.set_title(title, fontsize=13)
        ax.set_axis_off()
    fig.suptitle(
        "integracao monte carlo: mais amostras, menos ruido  ·  custo linear em spp",
        fontsize=17,
    )
    fig.text(
        0.5, 0.02,
        "entrada de referencia do relatorio: w=800, h=600, spp=32  →  T1 ≈ 54 s",
        ha="center", fontsize=12, color=MUTED,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    save(fig, "09_spp_comparacao.png")


def fig_unidade_trabalho():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_axis_off()
    ax.set_title("unidade de trabalho: uma linha da imagem")

    levels = [
        (0.4, 7.2, 15.2, 1.4, ACCENT,
         "laco externo  y = 0 .. h-1     ←  paralelizado com  #pragma omp for",
         "h = 600 linhas  (entrada de referencia)"),
        (1.1, 5.3, 13.8, 1.35, TEAL,
         "para cada linha:  x = 0 .. w-1",
         "w = 800 pixels  ·  escrita so em c[y·w + x]"),
        (1.8, 3.5, 12.4, 1.25, GOLD,
         "2 × 2 subpixels  (amostragem estratificada)",
         "4 subpixels por pixel"),
        (2.5, 1.6, 11.0, 1.25, RED,
         "s = 0 .. spp-1   →   radiance(raio)",
         "spp = 32  ·  98,2% do tempo (gprof) esta aqui"),
    ]
    for x, y, w, h, color, title, sub in levels:
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.18",
            facecolor="white", edgecolor=color, linewidth=2.2,
        ))
        ax.text(x + 0.35, y + h * 0.62, title, fontsize=14, color=INK, va="center")
        ax.text(x + 0.35, y + h * 0.28, sub, fontsize=12, color=MUTED, va="center")

    ax.text(
        8, 0.45,
        "600 × 800 × 4 × 32  =  61,4 milhoes de raios primarios   ·   cada um pode ricochetear dezenas de vezes",
        ha="center", fontsize=13, color=INK,
        bbox=dict(boxstyle="round,pad=0.35", fc="#f4f4f4", ec="#dddddd"),
    )
    save(fig, "10_unidade_trabalho.png")


def fig_eixo_paralelismo():
    img = read_ppm(OUT / "render_640x480_spp16.ppm")
    h, w = img.shape[:2]
    n = 6
    colors = ["#e76f51", "#f4a261", "#e9c46a", "#2a9d8f", "#264653", "#4a72b8"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 9), gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    ax.imshow(img)
    band = h // n
    for i, c in enumerate(colors):
        # y=0 no laco (e no buffer) e a base da imagem gravada no ppm.
        y0 = h - (i + 1) * band if i < n - 1 else 0
        y1 = h - i * band
        ax.add_patch(Rectangle(
            (0, y0), w, y1 - y0,
            facecolor=c, edgecolor="white", linewidth=1.2, alpha=0.32,
        ))
        ax.text(
            12, (y0 + y1) / 2, f"t{i}", color="white", fontsize=12,
            va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.15", fc=c, ec="none", alpha=0.92),
        )
    ax.set_axis_off()
    ax.set_title("static: faixas contiguas  ·  t0 pega y=0 (base da imagem)")

    ax2 = axes[1]
    ax2.imshow(img)
    chunk = 4
    for vis in range(0, h, chunk):
        buf_y = h - vis - chunk
        if buf_y < 0:
            buf_y = 0
        tid = (buf_y // chunk) % n
        ax2.add_patch(Rectangle(
            (0, vis), w, min(chunk, h - vis),
            facecolor=colors[tid], edgecolor="none", alpha=0.32,
        ))
    ax2.set_axis_off()
    ax2.set_title("dynamic,4: blocos de 4 linhas, pegos sob demanda")

    handles = [mpatches.Patch(color=c, label=f"thread {i}") for i, c in enumerate(colors)]
    fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False, fontsize=11)
    fig.suptitle(
        "eixo de paralelismo: cada linha e independente  ·  sem atomic / critical / reduction",
        fontsize=16, y=0.98,
    )
    save(fig, "11_eixo_paralelismo.png")


def fig_planta_cena():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_aspect("equal")
    ax.set_xlim(-40, 330)
    ax.set_ylim(-25, 125)
    ax.set_axis_off()
    ax.set_title("planta da cena (vista de cima)  ·  coordenadas do smallpt original")

    def xz(x, z):
        return z, x

    room = Rectangle((0, 1), 170, 98, facecolor="#f3f3f3", edgecolor=INK, lw=1.6)
    ax.add_patch(room)
    ax.add_patch(Rectangle((0, 1), 170, 3, facecolor=RED, edgecolor="none", alpha=0.9))
    ax.add_patch(Rectangle((0, 96), 170, 3, facecolor=BLUE, edgecolor="none", alpha=0.9))
    ax.add_patch(Rectangle((0, 1), 4, 98, facecolor="#d0d0d0", edgecolor="none"))

    ax.add_patch(Circle(xz(27, 47), 16.5, facecolor="#cfd8dc", edgecolor=INK, lw=1.5))
    ax.add_patch(Circle(xz(73, 78), 16.5, facecolor="#d6f0f5", edgecolor=TEAL, lw=1.5, alpha=0.9))
    ax.add_patch(Circle(xz(50, 81.6), 7, facecolor=GOLD, edgecolor="#b8860b", lw=1.2))

    ax.plot(*xz(50, 295.6), "o", color=INK, markersize=10)
    ax.annotate(
        "", xy=xz(50, 175), xytext=xz(50, 288),
        arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.8),
    )
    ax.plot([210, 210], [20, 80], color=MUTED, lw=1.3)
    ax.plot([205, 215], [20, 20], color=MUTED, lw=1.3)
    ax.plot([205, 215], [80, 80], color=MUTED, lw=1.3)
    ax.text(222, 50, "plano da\nimagem", ha="left", va="center", fontsize=11, color=MUTED)

    ax.text(*xz(27, 47), "spec\n(27, 16.5, 47)", ha="center", va="center", fontsize=10)
    ax.text(*xz(73, 78), "refr\n(73, 16.5, 78)", ha="center", va="center", fontsize=10)
    ax.text(81.6, 64, "luz", ha="center", fontsize=11)
    ax.text(295.6, 64, "camera\n(50, 52, 295.6)", ha="center", fontsize=12)
    ax.text(85, 8, "parede vermelha  x ≈ 1", ha="center", fontsize=11, color=RED)
    ax.text(85, 112, "parede azul  x ≈ 99", ha="center", fontsize=11, color=BLUE)
    ax.text(-12, 50, "fundo\nz = 0", ha="center", va="center", fontsize=11, color=MUTED)
    ax.text(175, 50, "frente\nz = 170", ha="left", va="center", fontsize=11, color=MUTED)
    ax.text(85, -16, "eixo z (profundidade)  →     sala ≈ 99 × 81.6 × 170", ha="center", fontsize=12)
    save(fig, "12_planta_cena.png")


def fig_gprof():
    groups = [
        ("sphere_intersect +\nintersect_scene", 31.24 + 5.08, ACCENT),
        ("ops. vetoriais\n(v_dot, v_norm, ...)", 11.93 + 10.50 + 7.72 + 6.59 + 4.19 + 2.61 + 1.29 + 0.94, TEAL),
        ("radiance\n(tempo proprio)", 14.02, GOLD),
        ("rng", 1.35 + 0.73, MUTED),
        ("main\n(setup + checksum)", 1.75, RED),
    ]
    labels = [g[0] for g in groups]
    vals = [g[1] for g in groups]
    colors = [g[2] for g in groups]
    fig, ax = plt.subplots(figsize=(16, 9))
    bars = ax.barh(labels[::-1], vals[::-1], color=colors[::-1], height=0.62)
    for bar, v in zip(bars, vals[::-1]):
        ax.text(v + 0.4, bar.get_y() + bar.get_height() / 2, f"{v:.1f}%",
                va="center", fontsize=13)
    ax.set_xlim(0, 55)
    ax.set_xlabel("tempo proprio do gprof (%)")
    ax.set_title("perfil sequencial  ·  w=800 h=600 spp=32  ·  f ≈ 0,982 esta no laco em y")
    ax.axvline(0, color="#dddddd")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(
        0.98, 0.08,
        "Smax(6) ≈ 5,51     Smax(12) ≈ 10,00     S∞ ≈ 55,6",
        transform=ax.transAxes, ha="right", fontsize=13, color=MUTED,
    )
    save(fig, "13_gprof.png")


def read_times(path, key="threads"):
    d = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            k = int(row[key]) if key == "threads" else row[key]
            d.setdefault(k, []).append(float(row["time_s"]))
    return d


def fig_speedup():
    strong = read_times(RESULTS / "strong.csv")
    xs = sorted(strong)
    med = [statistics.median(strong[p]) for p in xs]
    mn = [min(strong[p]) for p in xs]
    mx = [max(strong[p]) for p in xs]
    t1 = med[xs.index(1)]
    sp = [t1 / t for t in med]
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.plot(xs, xs, "--", color="0.55", label="ideal (y = p)")
    ax.plot(xs, sp, "o-", color=ACCENT, lw=2, markersize=8, label="medido (mediana)")
    ax.fill_between(xs, [t1 / m for m in mx], [t1 / n for n in mn],
                    color=ACCENT, alpha=0.15, label="min / max")
    ax.axvline(PHYSICAL_CORES, color="0.4", ls=":", lw=1.3)
    ax.text(PHYSICAL_CORES + 0.15, 1.3, "smt (>6 threads)", color=MUTED, rotation=90, va="bottom")
    ax.set_xlabel("numero de threads")
    ax.set_ylabel("speed-up")
    ax.set_title("escalabilidade forte  ·  w=800 h=600 spp=32  ·  10 execucoes")
    ax.set_xticks(xs)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "14_speedup.png")


def fig_efficiency():
    strong = read_times(RESULTS / "strong.csv")
    weak = read_times(RESULTS / "weak.csv")
    xs = sorted(strong)
    t1s = statistics.median(strong[1])
    sps = [t1s / statistics.median(strong[p]) for p in xs]
    efs = [s / p * 100 for s, p in zip(sps, xs)]
    xw = sorted(weak)
    t1w = statistics.median(weak[1])
    efw = [t1w / statistics.median(weak[p]) * 100 for p in xw]
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.plot(xs, efs, "o-", color=ACCENT, lw=2, markersize=8, label="forte  T1/(p·Tp)")
    ax.plot(xw, efw, "s-", color=GOLD, lw=2, markersize=8, label="fraca  T1/Tp")
    ax.axhline(100, color="0.55", ls="--", lw=1)
    ax.axvline(PHYSICAL_CORES, color="0.4", ls=":", lw=1.3)
    ax.text(PHYSICAL_CORES + 0.15, 8, "smt (>6 threads)", color=MUTED, rotation=90, va="bottom")
    ax.set_xlabel("numero de threads")
    ax.set_ylabel("eficiencia (%)")
    ax.set_title("eficiencia: forte vs fraca  ·  as duas curvas quebram no smt")
    ax.set_xticks(xs)
    ax.set_ylim(0, 110)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "15_eficiencia.png")


def fig_schedule():
    raw = {}
    with (RESULTS / "sched.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            raw.setdefault(row["schedule"], []).append(float(row["time_s"]))
    order = ["static", "static_32", "static_4", "dynamic", "dynamic_32", "dynamic_4", "guided"]
    labels = ["static", "static,32", "static,4", "dynamic", "dynamic,32", "dynamic,4\n(adotada)", "guided"]
    med = [statistics.median(raw[k]) for k in order]
    mn = [min(raw[k]) for k in order]
    mx = [max(raw[k]) for k in order]
    yerr = np.array([[m - a, b - m] for m, a, b in zip(med, mn, mx)]).T
    colors = [MUTED if k != "dynamic_4" else TEAL for k in order]
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.bar(labels, med, color=colors, yerr=yerr, capsize=4, width=0.62, ecolor=INK)
    ax.set_ylabel("mediana (s)")
    ax.set_title("politicas de escalonamento  ·  12 threads  ·  10 execucoes  ·  barra = min/max")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for x, m in zip(labels, med):
        ax.text(x, m + 0.18, f"{m:.2f}s", ha="center", fontsize=11)
    save(fig, "16_schedule.png")


def main():
    style()
    OUT.mkdir(parents=True, exist_ok=True)
    copy_assets()
    fig_cena_rotulada()
    fig_path_rotulado()
    fig_materiais_rotulado()
    fig_render_real()
    fig_spp_comparacao()
    fig_unidade_trabalho()
    fig_eixo_paralelismo()
    fig_planta_cena()
    fig_gprof()
    fig_speedup()
    fig_efficiency()
    fig_schedule()
    print("ok")


if __name__ == "__main__":
    main()
