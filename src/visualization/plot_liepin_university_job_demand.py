"""Plot Liepin university job demand report screenshots as reusable figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd


INPUT_CSV = Path("data/processed/liepin_university_job_demand_structure.csv")
OUTPUT_DIR = Path("reports/figures")

FIGURE_OUTPUTS = {
    "education_requirement": "liepin_job_education_requirement_distribution.png",
    "registered_capital": "liepin_job_registered_capital_distribution.png",
    "company_type": "liepin_job_company_type_distribution.png",
}

GROUP_TITLES = {
    "education_requirement": "大学生岗位学历要求：本科仍占六成以上，硕士占比回落",
    "registered_capital": "按企业注册资本看大学生需求：中等规模企业占比最高",
    "company_type": "分企业性质看大学生需求：私营/民营企业接近一半",
}

GROUP_SUBTITLES = {
    "education_requirement": "2024后半年 vs 2025前半年，单位为岗位需求占比",
    "registered_capital": "注册资本区间反映需求企业规模结构，不等同于岗位质量",
    "company_type": "企业性质用于观察需求端主体结构，不等同于毕业生最终去向",
}

PERIOD_ORDER = ["2024H2", "2025H1"]
PERIOD_COLORS = {
    "2024H2": "#72C34B",
    "2025H1": "#FF6A00",
}

COLORS = {
    "ink": "#202124",
    "muted": "#6B7280",
    "grid": "#E5E7EB",
    "paper": "#FAFAF7",
}


def plot_liepin_university_job_demand(
    input_csv: Path = INPUT_CSV,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Path]:
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    _set_chinese_font()

    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for group, filename in FIGURE_OUTPUTS.items():
        output_path = output_dir / filename
        _plot_group(df[df["indicator_group"] == group].copy(), group, output_path)
        written[group] = output_path
    return written


def _plot_group(data: pd.DataFrame, group: str, output_path: Path) -> None:
    data = data.sort_values(["category_order", "period"])
    categories = (
        data[["category_order", "category"]]
        .drop_duplicates()
        .sort_values("category_order")["category"]
        .tolist()
    )
    period_labels = (
        data[["period", "period_label"]]
        .drop_duplicates()
        .set_index("period")["period_label"]
        .to_dict()
    )

    fig, ax = plt.subplots(figsize=(11.2, 6.5 if group != "company_type" else 7.0), dpi=160)
    fig.patch.set_facecolor(COLORS["paper"])
    ax.set_facecolor(COLORS["paper"])

    x_positions = np.arange(len(categories))
    bar_width = 0.34
    max_value = float(data["percentage"].max())

    for period_index, period in enumerate(PERIOD_ORDER):
        period_data = data[data["period"] == period].set_index("category").loc[categories]
        offset = (period_index - 0.5) * bar_width
        bars = ax.bar(
            x_positions + offset,
            period_data["percentage"],
            width=bar_width,
            label=period_labels.get(period, period),
            color=PERIOD_COLORS[period],
            edgecolor="white",
            linewidth=0.9,
        )
        _label_bars(ax, bars, max_value)

    wrapped_labels = [_wrap_label(label, 7 if group == "company_type" else 10) for label in categories]
    ax.set_xticks(x_positions)
    ax.set_xticklabels(wrapped_labels, fontsize=10, color=COLORS["ink"])
    ax.set_ylim(0, max_value * 1.22)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}%"))
    ax.set_ylabel("岗位需求占比", color=COLORS["muted"], fontsize=10.5)
    ax.tick_params(axis="y", colors=COLORS["muted"], labelsize=10)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.9)
    ax.grid(axis="x", visible=False)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#D1D5DB")

    _add_title(ax, GROUP_TITLES[group], GROUP_SUBTITLES[group])
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0, 1.02), ncol=2, fontsize=10)
    ax.text(
        0,
        -0.22 if group != "company_type" else -0.25,
        "数据来源：《2025届大学生就业供需洞察报告》",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color=COLORS["muted"],
    )

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=180)
    plt.close(fig)


def _label_bars(ax: plt.Axes, bars, max_value: float) -> None:
    for bar in bars:
        value = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + max_value * 0.018,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9.2,
            color=COLORS["ink"],
        )


def _wrap_label(label: str, width: int) -> str:
    if len(label) <= width:
        return label
    return "\n".join(label[index : index + width] for index in range(0, len(label), width))


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


def _add_title(ax: plt.Axes, title: str, subtitle: str) -> None:
    ax.text(
        0,
        1.18,
        title,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=18,
        fontweight="bold",
        color=COLORS["ink"],
    )
    ax.text(
        0,
        1.105,
        subtitle,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=10.5,
        color=COLORS["muted"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot Liepin university job demand figures")
    parser.add_argument("--input", type=Path, default=INPUT_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    written = plot_liepin_university_job_demand(args.input, args.output_dir)
    for output_path in written.values():
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
