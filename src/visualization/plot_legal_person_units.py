"""Plot legal-person-unit industry trends and province-industry structure."""

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


INPUT_INDUSTRY_YEAR = Path("data/processed/legal_person_units_by_industry_year_panel.csv")
INPUT_PROVINCE_INDUSTRY = Path("data/processed/legal_person_units_by_province_industry_2024.csv")
OUTPUT_TREND = Path("reports/figures/legal_person_units_industry_growth_trend.png")
OUTPUT_HEATMAP = Path("reports/figures/legal_person_units_province_industry_heatmap_2024.png")

TREND_RANK_YEAR = 2024
TREND_TOP_N = 10
TREND_LABEL_YEAR = 2020
TREND_ENDPOINT_LABEL_YEAR = 2024
TREND_HIGHLIGHT_MAX_N = 6
TREND_HIGHLIGHT_PRIORITY = [
    "wholesale_retail",
    "leasing_business_services",
    "manufacturing",
    "construction",
    "scientific_research_technical_services",
    "information_software_it",
]

TREND_PALETTE = [
    "#0B5D7E",
    "#1F7A3A",
    "#9A5A00",
    "#B91C1C",
    "#6A5ACD",
    "#C2410C",
    "#455A64",
    "#8B5CF6",
    "#D97706",
    "#64748B",
]

SHORT_INDUSTRY_LABELS = {
    "agriculture_forestry_animal_fishing": "农林牧渔",
    "manufacturing": "制造业",
    "construction": "建筑业",
    "wholesale_retail": "批发零售",
    "transport_storage_postal": "交通运输",
    "information_software_it": "信息服务",
    "real_estate": "房地产",
    "leasing_business_services": "商务服务",
    "scientific_research_technical_services": "科研技术",
    "public_management_social_security_social_org": "公共管理",
}

HEATMAP_PROVINCES = ["北京市", "上海市", "江苏省", "浙江省", "广东省", "湖北省", "四川省", "山东省", "河南省"]
HEATMAP_INDUSTRIES = [
    "manufacturing",
    "wholesale_retail",
    "information_software_it",
    "leasing_business_services",
    "scientific_research_technical_services",
    "education",
    "construction",
    "culture_sports_entertainment",
]

COLORS = {
    "ink": "#202124",
    "muted": "#6B7280",
    "grid": "#E5E7EB",
    "manufacturing": "#455A64",
    "wholesale_retail": "#1F7A3A",
    "information_software_it": "#0B5D7E",
    "leasing_business_services": "#9A5A00",
    "scientific_research_technical_services": "#B91C1C",
}

TREND_HIGHLIGHT_COLORS = {
    "wholesale_retail": "#1F7A3A",
    "leasing_business_services": "#9A5A00",
    "manufacturing": "#455A64",
    "construction": "#C2410C",
    "scientific_research_technical_services": "#B91C1C",
    "information_software_it": "#0B5D7E",
}


def plot_industry_growth_trend(
    input_csv: Path = INPUT_INDUSTRY_YEAR,
    output_figure: Path = OUTPUT_TREND,
) -> None:
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    rank_industries = select_top_industries_by_year(df)
    trend_industries = select_trend_highlight_industries(df, rank_industries)
    included_industries = list(dict.fromkeys(trend_industries + rank_industries))
    BASE_YEAR = 2020

    data = df[df["industry_code"].isin(included_industries)].copy()
    data = data.dropna(subset=["legal_person_units"])
    data["year"] = data["year"].astype(int)

    base_values = (
        data[data["year"] == BASE_YEAR][["industry_code", "legal_person_units"]]
        .rename(columns={"legal_person_units": "base_legal_person_units"})
    )

    missing_base_industries = sorted(set(data["industry_code"]) - set(base_values["industry_code"]))
    if missing_base_industries:
        raise ValueError(f"Missing {BASE_YEAR} base year data for industries: {missing_base_industries}")

    data = data.merge(base_values, on="industry_code", how="left")

    data["growth_index"] = (
        data["legal_person_units"] / data["base_legal_person_units"] * 100
    )

    data = data[data["year"] >= BASE_YEAR].copy()

    _set_chinese_font()
    fig = plt.figure(figsize=(14.2, 7.2), dpi=160)
    grid = fig.add_gridspec(1, 2, width_ratios=[3.9, 1.25], wspace=0.08)
    ax = fig.add_subplot(grid[0, 0])
    rank_ax = fig.add_subplot(grid[0, 1])
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    for index, industry_code in enumerate(trend_industries):
        series = data[data["industry_code"] == industry_code].sort_values("year")
        label = _short_industry_label(industry_code, series["industry_name"].iloc[0])
        ax.plot(
            series["year"],
            series["growth_index"],
            color=_industry_color(industry_code, index),
            linewidth=3.1,
            marker="o",
            markersize=4.6,
            label=label,
        )

    _add_title(
        fig,
        "行业主体结构：增长路径和规模排名",
        "左图是几个重点行业2020-2024年增长路径；右图为2024年数量规模 Top 10行业排序",
    )
    _style_trend_axes(ax)
    # _add_trend_year_labels(ax, data, trend_industries, TREND_LABEL_YEAR)
    _add_trend_endpoint_labels(ax, data, trend_industries, TREND_ENDPOINT_LABEL_YEAR)
    _add_2024_quantity_panel(rank_ax, data, rank_industries, trend_industries)
    _add_trend_source_note(fig)

    fig.subplots_adjust(left=0.07, right=0.97, top=0.84, bottom=0.12, wspace=0.14)
    output_figure.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_figure, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def select_top_industries_by_year(
    df: pd.DataFrame,
    rank_year: int = TREND_RANK_YEAR,
    top_n: int = TREND_TOP_N,
) -> list[str]:
    ranked = (
        df[(df["year"] == rank_year) & (df["industry_code"] != "total")]
        .dropna(subset=["legal_person_units"])
        .sort_values("legal_person_units", ascending=False)
    )
    return ranked.head(top_n)["industry_code"].tolist()


def select_trend_highlight_industries(
    df: pd.DataFrame,
    ranked_industries: list[str] | None = None,
    max_n: int = TREND_HIGHLIGHT_MAX_N,
) -> list[str]:
    ranked = ranked_industries or select_top_industries_by_year(df)
    ranked_set = set(ranked)
    selected = [industry for industry in TREND_HIGHLIGHT_PRIORITY if industry in ranked_set]
    if len(selected) < max_n:
        selected.extend([industry for industry in ranked if industry not in selected])
    return selected[:max_n]


def format_quantity_panel_label(legal_person_units: float) -> str:
    return f"{legal_person_units / 10_000:.0f}"


def plot_province_industry_heatmap(
    input_csv: Path = INPUT_PROVINCE_INDUSTRY,
    output_figure: Path = OUTPUT_HEATMAP,
) -> None:
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    data = df[
        df["province"].isin(HEATMAP_PROVINCES) & df["industry_code"].isin(HEATMAP_INDUSTRIES)
    ].copy()
    data["industry_label"] = data["industry_name"].replace(
        {
            "信息传输、软件和信息技术服务业": "信息服务",
            "租赁和商务服务业": "商务服务",
            "科学研究和技术服务业": "科研技术",
            "文化、体育和娱乐业": "文体娱乐",
            "批发和零售业": "批发零售",
        }
    )
    pivot = data.pivot(index="province", columns="industry_label", values="industry_share")
    province_order = [province for province in HEATMAP_PROVINCES if province in pivot.index]
    industry_order = [
        "制造业",
        "批发零售",
        "信息服务",
        "商务服务",
        "科研技术",
        "教育",
        "建筑业",
        "文体娱乐",
    ]
    pivot = pivot.loc[province_order, industry_order]

    _set_chinese_font()
    fig, ax = plt.subplots(figsize=(11.2, 6.8), dpi=160)
    fig.patch.set_facecolor("#FFFFFF")

    values = pivot.to_numpy(dtype=float)
    image = ax.imshow(values, cmap="YlGnBu", aspect="auto", vmin=0, vmax=np.nanmax(values))

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=10, color=COLORS["ink"])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=10, color=COLORS["ink"])
    ax.tick_params(top=False, bottom=False, left=False)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for row_index in range(values.shape[0]):
        for col_index in range(values.shape[1]):
            value = values[row_index, col_index]
            text_color = "#FFFFFF" if value > np.nanmax(values) * 0.58 else COLORS["ink"]
            ax.text(
                col_index,
                row_index,
                f"{value * 100:.1f}%",
                ha="center",
                va="center",
                fontsize=8.8,
                color=text_color,
            )

    _add_title(
        fig,
        "2024年重点地区法人单位行业结构",
        "数值为该省级地区各行业法人单位数占本地区法人单位总数的比例",
    )
    colorbar = fig.colorbar(image, ax=ax, shrink=0.82, pad=0.018)
    colorbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value * 100:.0f}%"))
    colorbar.ax.tick_params(labelsize=9, colors=COLORS["muted"])
    colorbar.outline.set_visible(False)
    _add_heatmap_source_note(fig)

    fig.tight_layout(rect=[0.04, 0.08, 0.96, 0.88])
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
    fig.text(0.055, 0.955, title, fontsize=24, fontweight="bold", color=COLORS["ink"])
    fig.text(0.055, 0.908, subtitle, fontsize=12, color=COLORS["muted"])


def _style_trend_axes(ax: plt.Axes) -> None:
    ax.grid(axis="y", color=COLORS["grid"], linewidth=1)
    ax.grid(axis="x", visible=False)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#CBD5E1")
    ax.set_xlim(2020, 2024.8)
    ax.set_xticks([2020, 2021, 2022, 2023, 2024])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{int(value)}"))
    ax.tick_params(axis="both", colors=COLORS["muted"], labelsize=10.5)
    ax.set_ylabel("增长指数（2020=100）", color=COLORS["muted"], fontsize=11)


def _add_trend_year_labels(
    ax: plt.Axes,
    data: pd.DataFrame,
    trend_industries: list[str],
    label_year: int,
) -> None:
    label_rows = (
        data[data["year"] == label_year]
        .set_index("industry_code")
        .loc[trend_industries]
        .sort_values("growth_index")
    )
    offsets = [-20, -12, -4, 4, 12, 20, -26, 26, -32, 32]
    for index, (industry_code, row) in enumerate(label_rows.iterrows()):
        ax.annotate(
            f"2020: {row['growth_index']:.0f}",
            xy=(label_year, row["growth_index"]),
            xytext=(-10, offsets[index % len(offsets)]),
            textcoords="offset points",
            ha="right",
            va="center",
            fontsize=7.6,
            color=_industry_color(industry_code, trend_industries.index(industry_code)),
            bbox={
                "boxstyle": "round,pad=0.22",
                "facecolor": "#FFFFFF",
                "edgecolor": "#E5E7EB",
                "linewidth": 0.8,
                "alpha": 0.92,
            },
        )


def _add_trend_endpoint_labels(
    ax: plt.Axes,
    data: pd.DataFrame,
    trend_industries: list[str],
    label_year: int,
) -> None:
    label_rows = (
        data[data["year"] == label_year]
        .set_index("industry_code")
        .loc[trend_industries]
        .sort_values("growth_index")
    )
    offsets = [-22, -8, 8, 24, 40, 56]
    for index, (industry_code, row) in enumerate(label_rows.iterrows()):
        label = _short_industry_label(industry_code, row["industry_name"])
        color = _industry_color(industry_code, trend_industries.index(industry_code))
        ax.annotate(
            f"{label} {row['growth_index']:.0f}",
            xy=(label_year, row["growth_index"]),
            xytext=(12, offsets[index % len(offsets)]),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9.2,
            color=color,
            fontweight="bold",
            arrowprops={"arrowstyle": "-", "color": color, "lw": 1.1, "alpha": 0.85},
        )


def _add_2024_quantity_panel(
    ax: plt.Axes,
    data: pd.DataFrame,
    rank_industries: list[str],
    highlighted_industries: list[str],
) -> None:
    ranking = (
        data[data["year"] == TREND_RANK_YEAR]
        .set_index("industry_code")
        .loc[rank_industries]
        .copy()
    )
    ranking["label"] = [
        _short_industry_label(industry_code, row["industry_name"])
        for industry_code, row in ranking.iterrows()
    ]
    ranking["units_10k"] = ranking["legal_person_units"] / 10_000

    y_positions = np.arange(len(ranking))
    colors = [
        _industry_color(industry_code, index)
        if industry_code in highlighted_industries
        else "#CBD5E1"
        for index, industry_code in enumerate(ranking.index)
    ]
    ax.barh(y_positions, ranking["units_10k"], color=colors, height=0.58)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(ranking["label"], fontsize=8.8, color=COLORS["ink"])
    ax.invert_yaxis()
    ax.set_title("2024实际数量Top10\n（万个）", fontsize=11, color=COLORS["ink"], fontweight="bold", pad=10)
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.tick_params(axis="x", colors=COLORS["muted"], labelsize=8.5)
    ax.tick_params(axis="y", length=0)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#CBD5E1")

    max_value = ranking["units_10k"].max()
    ax.set_xlim(0, max_value * 1.22)
    for y_position, value in zip(y_positions, ranking["units_10k"]):
        ax.text(
            value + max_value * 0.025,
            y_position,
            format_quantity_panel_label(value * 10_000),
            va="center",
            ha="left",
            fontsize=8.4,
            color=COLORS["muted"],
        )


def _short_industry_label(industry_code: str, fallback: str) -> str:
    return SHORT_INDUSTRY_LABELS.get(industry_code, fallback)


def _industry_color(industry_code: str, index: int) -> str:
    return TREND_HIGHLIGHT_COLORS.get(industry_code, _trend_color(index))


def _trend_color(index: int) -> str:
    return TREND_PALETTE[index % len(TREND_PALETTE)]


def _add_trend_source_note(fig: plt.Figure) -> None:
    fig.text(
        0.055,
        0.035,
        "数据来源：截图《1-5 分地区按主要行业分法人单位数》人工转录；截图转录数据需二次核对",
        fontsize=9.5,
        color=COLORS["muted"],
    )


def _add_heatmap_source_note(fig: plt.Figure) -> None:
    fig.text(
        0.055,
        0.035,
        "数据来源：截图《1-5 分地区按主要行业分法人单位数》人工转录；地区为省级地区，非城市明细",
        fontsize=9.5,
        color=COLORS["muted"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot legal person unit figures")
    parser.add_argument("--industry-year-input", type=Path, default=INPUT_INDUSTRY_YEAR)
    parser.add_argument("--province-industry-input", type=Path, default=INPUT_PROVINCE_INDUSTRY)
    parser.add_argument("--trend-output", type=Path, default=OUTPUT_TREND)
    parser.add_argument("--heatmap-output", type=Path, default=OUTPUT_HEATMAP)
    args = parser.parse_args()

    plot_industry_growth_trend(args.industry_year_input, args.trend_output)
    plot_province_industry_heatmap(args.province_industry_input, args.heatmap_output)
    print(f"Wrote {args.trend_output}")
    print(f"Wrote {args.heatmap_output}")


if __name__ == "__main__":
    main()
