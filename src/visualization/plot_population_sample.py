"""Plot youth age-group shares from the population sample panel."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
import pandas as pd


INPUT_CSV = Path("data/processed/population_sample_age_panel.csv")
OUTPUT_FIGURE = Path("reports/figures/youth_population_sample_share_trend.png")

COLORS = {
    "ink": "#202124",
    "muted": "#6B7280",
    "grid": "#E5E7EB",
    "paper": "#FAFAF7",
    "blue": "#1F6F8B",
    "green": "#2E7D32",
}


def plot_youth_population_share(input_csv: Path = INPUT_CSV, output_figure: Path = OUTPUT_FIGURE) -> None:
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    pivot = (
        df[df["age_group"].isin(["20-24岁", "20-29岁"])]
        .pivot(index="year", columns="age_group", values="age_group_share")
        .sort_index()
    )

    _set_chinese_font()
    fig, ax = _setup_figure()

    ax.plot(
        pivot.index,
        pivot["20-29岁"],
        color=COLORS["blue"],
        linewidth=3.2,
        marker="o",
        markersize=5.5,
        label="20-29岁样本占比",
    )
    ax.plot(
        pivot.index,
        pivot["20-24岁"],
        color=COLORS["green"],
        linewidth=2.6,
        marker="o",
        markersize=5,
        label="20-24岁样本占比",
    )

    ax.fill_between(pivot.index, pivot["20-29岁"], color=COLORS["blue"], alpha=0.09)

    _add_title(
        ax,
        "青年人口样本占比并未上升",
        "人口抽样调查样本中，20-29岁占比从 2016 年 16.04% 降至 2024 年 10.57%",
    )

    share_2016 = pivot.loc[2016, "20-29岁"]
    share_2024 = pivot.loc[2024, "20-29岁"]
    share_20_24_2016 = pivot.loc[2016, "20-24岁"]
    share_20_24_2024 = pivot.loc[2024, "20-24岁"]

    _annotate_endpoint(ax, 2016, share_2016, f"2016：{share_2016:.2%}", COLORS["blue"], (-5, 10))
    _annotate_endpoint(ax, 2024, share_2024, f"2024：{share_2024:.2%}", COLORS["blue"], (12, 0))
    _annotate_endpoint(
        ax,
        2016,
        share_20_24_2016,
        f"20-24岁：{share_20_24_2016:.2%}",
        COLORS["green"],
        (8, -18),
    )
    _annotate_endpoint(
        ax,
        2024,
        share_20_24_2024,
        f"20-24岁：{share_20_24_2024:.2%}",
        COLORS["green"],
        (12, -14),
    )

    ax.annotate(
        "这组数据用于排除误解：\n毕业生供给上升，不等于青年人口占比上升",
        xy=(2024, share_2024),
        xytext=(2017.6, 0.17),
        arrowprops=dict(arrowstyle="->", color=COLORS["blue"], lw=1.5),
        bbox=dict(boxstyle="round,pad=0.48", fc="white", ec="#C7DDE8", lw=1.0),
        fontsize=12,
        color=COLORS["blue"],
        fontweight="bold",
    )

    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))
    ax.set_ylabel("样本占比", color=COLORS["muted"])
    ax.set_xticks(range(2016, 2025))
    ax.set_ylim(0.045, 0.19)
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    ax.text(
        0,
        -0.18,
        "数据来源：人口抽样调查样本数据_年度数据.xlsx；该数据为抽样调查样本，仅用于观察年龄结构占比变化",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color=COLORS["muted"],
    )

    output_figure.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_figure, bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=180)
    plt.close(fig)


def _set_chinese_font() -> None:
    candidates = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "Arial Unicode MS",
    ]
    available = {
        font_manager.FontProperties(fname=font_path).get_name()
        for font_path in font_manager.findSystemFonts()
    }
    for candidate in candidates:
        if candidate in available:
            plt.rcParams["font.sans-serif"] = [candidate, "DejaVu Sans"]
            break
    plt.rcParams["axes.unicode_minus"] = False


def _setup_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(11, 6.2), dpi=160)
    fig.patch.set_facecolor(COLORS["paper"])
    ax.set_facecolor(COLORS["paper"])
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#D1D5DB")
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.9)
    ax.grid(axis="x", visible=False)
    ax.tick_params(axis="both", colors=COLORS["muted"], labelsize=10)
    return fig, ax


def _add_title(ax: plt.Axes, title: str, subtitle: str) -> None:
    ax.text(
        0,
        1.12,
        title,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=20,
        fontweight="bold",
        color=COLORS["ink"],
    )
    ax.text(
        0,
        1.055,
        subtitle,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=11,
        color=COLORS["muted"],
    )


def _annotate_endpoint(
    ax: plt.Axes,
    x: int,
    y: float,
    label: str,
    color: str,
    offset: tuple[int, int],
) -> None:
    ax.scatter([x], [y], s=54, color=color, edgecolor="white", linewidth=1.5, zorder=5)
    ax.annotate(
        label,
        xy=(x, y),
        xytext=offset,
        textcoords="offset points",
        fontsize=10.5,
        color=color,
        fontweight="bold",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot youth population sample shares")
    parser.add_argument("--input", type=Path, default=INPUT_CSV)
    parser.add_argument("--output", type=Path, default=OUTPUT_FIGURE)
    args = parser.parse_args()

    plot_youth_population_share(args.input, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
