"""Plot province-level enterprise legal person units for key regions."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
import pandas as pd


INPUT_CSV = Path("data/processed/enterprise_units_by_province_panel.csv")
OUTPUT_FIGURE = Path("reports/figures/enterprise_units_key_regions_trend.png")

KEY_REGIONS = [
    "广东省",
    "江苏省",
    "浙江省",
    "湖北省",
    "四川省",
    "北京市",
    "上海市",
]

REGION_LABELS = {
    "广东省": "广东（深圳）",
    "江苏省": "江苏",
    "浙江省": "浙江（杭州）",
    "湖北省": "湖北（武汉）",
    "四川省": "四川（成都）",
    "北京市": "北京",
    "上海市": "上海",
}

COLORS = {
    "广东省": "#0B5D7E",
    "江苏省": "#1F7A3A",
    "浙江省": "#9A5A00",
    "湖北省": "#6A5ACD",
    "四川省": "#C2410C",
    "北京市": "#334155",
    "上海市": "#B91C1C",
    "ink": "#202124",
    "muted": "#6B7280",
    "grid": "#E5E7EB",
}


def plot_key_region_enterprise_units(
    input_csv: Path = INPUT_CSV,
    output_figure: Path = OUTPUT_FIGURE,
) -> None:
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    data = df[df["province"].isin(KEY_REGIONS)].copy()
    data["enterprise_units_10k"] = data["enterprise_legal_person_units"] / 10_000

    pivot = (
        data.pivot(index="year", columns="province", values="enterprise_units_10k")
        .sort_index()
        .loc[:, KEY_REGIONS]
    )

    _set_chinese_font()
    fig, ax = plt.subplots(figsize=(11.5, 6.4), dpi=160)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    for province in KEY_REGIONS:
        linewidth = 3.1 if province in {"广东省", "江苏省", "浙江省"} else 2.1
        alpha = 1.0 if province in {"广东省", "江苏省", "浙江省"} else 0.72
        ax.plot(
            pivot.index,
            pivot[province],
            color=COLORS[province],
            linewidth=linewidth,
            marker="o",
            markersize=5,
            alpha=alpha,
            label=REGION_LABELS[province],
        )

    _add_title(
        fig,
        "企业法人单位数的地区分化",
        "省级企业法人单位存量可作为岗位承载能力的背景变量，不能直接等同于招聘岗位数",
    )
    _style_axes(ax)
    _add_endpoint_labels(ax, pivot)
    _add_callout(ax)
    _add_source_note(fig)

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.02, 0.93),
        frameon=False,
        ncol=2,
        fontsize=10,
        labelcolor=COLORS["ink"],
        handlelength=2.6,
        columnspacing=1.4,
    )

    fig.tight_layout(rect=[0.04, 0.08, 0.98, 0.88])
    output_figure.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_figure, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def _set_chinese_font() -> None:
    candidates = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "Arial Unicode MS",
    ]
    available = {font.name for font in font_manager.fontManager.ttflist}
    for candidate in candidates:
        if candidate in available:
            plt.rcParams["font.sans-serif"] = [candidate]
            break
    plt.rcParams["axes.unicode_minus"] = False


def _add_title(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.055, 0.955, title, fontsize=25, fontweight="bold", color=COLORS["ink"])
    fig.text(0.055, 0.908, subtitle, fontsize=12.5, color=COLORS["muted"])


def _style_axes(ax: plt.Axes) -> None:
    ax.grid(axis="y", color=COLORS["grid"], linewidth=1)
    ax.grid(axis="x", visible=False)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#CBD5E1")

    ax.set_xlim(2015.7, 2024.9)
    ax.set_xticks([2016, 2017, 2019, 2020, 2021, 2022, 2024])
    ax.tick_params(axis="both", colors=COLORS["muted"], labelsize=10.5)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}万"))
    ax.set_ylabel("企业法人单位数", color=COLORS["muted"], fontsize=11)


def _add_endpoint_labels(ax: plt.Axes, pivot: pd.DataFrame) -> None:
    label_offsets = {
        "广东省": 0,
        "江苏省": 8,
        "浙江省": -9,
        "湖北省": 8,
        "四川省": -9,
        "北京市": 7,
        "上海市": -8,
    }
    final_year = int(pivot.index.max())
    for province in KEY_REGIONS:
        value = pivot.loc[final_year, province]
        ax.annotate(
            f"{REGION_LABELS[province]} {value:.0f}万",
            xy=(final_year, value),
            xytext=(10, label_offsets[province]),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9.5,
            color=COLORS[province],
            fontweight="bold" if province in {"广东省", "江苏省", "浙江省"} else "normal",
        )


def _add_callout(ax: plt.Axes) -> None:
    ax.text(
        2018.2,
        ax.get_ylim()[1] * 0.84,
        "用于解释地区背景：\n企业主体越集中，潜在岗位承载能力通常越强；\n但它不是岗位数，也不代表应届岗位质量。",
        fontsize=11,
        color=COLORS["ink"],
        bbox={
            "boxstyle": "round,pad=0.55",
            "facecolor": "#FFFFFF",
            "edgecolor": "#CBD5E1",
            "linewidth": 1.2,
        },
    )


def _add_source_note(fig: plt.Figure) -> None:
    fig.text(
        0.055,
        0.035,
        "数据来源：国家统计局，企业法人单位数_分省年度数据.xlsx；原表缺少2018、2023年",
        fontsize=9.5,
        color=COLORS["muted"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot key-region enterprise units trend")
    parser.add_argument("--input", type=Path, default=INPUT_CSV)
    parser.add_argument("--output", type=Path, default=OUTPUT_FIGURE)
    args = parser.parse_args()

    plot_key_region_enterprise_units(args.input, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
