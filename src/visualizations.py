"""
Python replications of the Tableau dashboard charts.
Run standalone: python src/visualizations.py
All charts saved to data/charts/.
"""

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

# ── common style ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi":        120,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
})

DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")
CHART_DIR = os.path.join(DATA_DIR, "charts")
os.makedirs(CHART_DIR, exist_ok=True)

REGION_PALETTE = {
    "Nordic":   "#2c3e50",
    "Western":  "#2980b9",
    "Southern": "#e74c3c",
    "Eastern":  "#f39c12",
}


def load() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "sample_processed.csv"))


def save(name: str) -> None:
    path = os.path.join(CHART_DIR, f"{name}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")


# ── Chart 1: Labour Market vs AI Adoption ────────────────────────────────────

def chart_unemployment_vs_adoption(df: pd.DataFrame) -> None:
    data = df[df["Company_Size"] == "Large"].drop_duplicates(
        subset=["Country_Code", "Year"]
    )

    lmh_palette = {"Stable": "#2ecc71", "Moderate": "#f39c12", "Fragile": "#e74c3c"}

    fig, ax = plt.subplots(figsize=(10, 6))
    for label, grp in data.groupby("Labour_Market_Health"):
        ax.scatter(grp["Unemployment_Rate"], grp["AI_Adoption_Pct"],
                   label=label, color=lmh_palette.get(label, "grey"),
                   s=80, alpha=0.8, edgecolors="white", linewidth=0.5)
        for _, row in grp.iterrows():
            ax.annotate(row["Country_Code"], (row["Unemployment_Rate"], row["AI_Adoption_Pct"]),
                        textcoords="offset points", xytext=(4, 2), fontsize=7, color="#555")

    # Trend line
    slope, intercept, r, p, _ = stats.linregress(
        data["Unemployment_Rate"], data["AI_Adoption_Pct"]
    )
    xs = np.linspace(data["Unemployment_Rate"].min(), data["Unemployment_Rate"].max(), 100)
    ax.plot(xs, slope * xs + intercept, "--", color="black", lw=1.5,
            label=f"Trend (R²={r**2:.2f}, slope={slope:.2f})")

    ax.set_xlabel("Unemployment Rate (%)")
    ax.set_ylabel("AI Adoption (%)")
    ax.set_title("Labour Market vs Enterprise AI Adoption in Europe")
    ax.legend(fontsize=9)
    save("chart1_unemployment_vs_adoption")


# ── Chart 2: Digital Skills vs AI Adoption ───────────────────────────────────

def chart_skills_vs_adoption(df: pd.DataFrame) -> None:
    data = df[df["Company_Size"] == "Large"].drop_duplicates(
        subset=["Country_Code", "Year"]
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    for region, grp in data.groupby("Region"):
        ax.scatter(grp["Digital_Skills_Index"], grp["AI_Adoption_Pct"],
                   label=region, color=REGION_PALETTE.get(region, "grey"),
                   s=80, alpha=0.8, edgecolors="white", linewidth=0.5)

    slope, intercept, r, _, _ = stats.linregress(
        data["Digital_Skills_Index"], data["AI_Adoption_Pct"]
    )
    xs = np.linspace(data["Digital_Skills_Index"].min(), data["Digital_Skills_Index"].max(), 100)
    ax.plot(xs, slope * xs + intercept, "--", color="black", lw=1.5,
            label=f"Trend (R²={r**2:.2f})")

    ax.set_xlabel("Digital Skills Index")
    ax.set_ylabel("AI Adoption (%)")
    ax.set_title("Digital Skills vs Enterprise AI Adoption in Europe")
    ax.legend(fontsize=9)
    save("chart2_skills_vs_adoption")


# ── Chart 3: AI Adoption by Country (Horizontal Bar) ─────────────────────────

def chart_adoption_by_country(df: pd.DataFrame) -> None:
    data = (
        df[(df["Company_Size"] == "Large") & (df["Year"] == 2024)]
        .groupby(["Country_Code", "Region"])["AI_Adoption_Pct"]
        .mean()
        .reset_index()
        .sort_values("AI_Adoption_Pct", ascending=True)
    )

    colors = [REGION_PALETTE.get(r, "grey") for r in data["Region"]]

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(data["Country_Code"], data["AI_Adoption_Pct"],
                   color=colors, edgecolor="none", height=0.7)

    for bar, val in zip(bars, data["AI_Adoption_Pct"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9)

    patches = [mpatches.Patch(color=v, label=k) for k, v in REGION_PALETTE.items()]
    ax.legend(handles=patches, fontsize=9)
    ax.set_xlabel("AI Adoption (%)")
    ax.set_title("Enterprise AI Adoption by Country — 2024 (Large Enterprises)")
    save("chart3_adoption_by_country")


# ── Chart 4: AI Adoption by Company Size ─────────────────────────────────────

def chart_adoption_by_size(df: pd.DataFrame) -> None:
    data = (
        df.groupby(["Company_Size", "Year"])["AI_Adoption_Pct"]
        .mean()
        .reset_index()
    )
    pivot = data.pivot(index="Company_Size", columns="Year", values="AI_Adoption_Pct")

    fig, ax = plt.subplots(figsize=(8, 5))
    pivot.plot(kind="bar", ax=ax, color=["#3498db", "#2c3e50"], width=0.6,
               edgecolor="none")

    ax.set_xlabel("Company Size")
    ax.set_ylabel("Mean AI Adoption (%)")
    ax.set_title("AI Adoption by Enterprise Size — 2024 vs 2025")
    ax.legend(title="Year", fontsize=9)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    save("chart4_adoption_by_size")


# ── Chart 5: AI Adoption by Sector (Treemap via heatmap proxy) ───────────────

def chart_adoption_by_sector(df: pd.DataFrame) -> None:
    data = (
        df.groupby(["NACE_Sector", "Region"])["AI_Adoption_Pct"]
        .mean()
        .reset_index()
    )
    pivot = data.pivot(index="NACE_Sector", columns="Region", values="AI_Adoption_Pct")
    pivot = pivot.fillna(0)

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(pivot, cmap="Blues", annot=True, fmt=".1f",
                linewidths=0.5, cbar_kws={"label": "AI Adoption (%)"}, ax=ax)
    ax.set_title("AI Adoption by Sector and Region (%)")
    ax.set_xlabel("Region")
    ax.set_ylabel("NACE Sector")
    save("chart5_adoption_by_sector")


# ── Chart 6: Digital Divide Quadrant ─────────────────────────────────────────

def chart_digital_divide_quadrant(df: pd.DataFrame) -> None:
    data = (
        df[df["Year"] == 2024]
        .groupby(["Country_Code", "Region"])[["Digital_Skills_Index", "AI_Adoption_Pct"]]
        .mean()
        .reset_index()
    )

    med_skills   = data["Digital_Skills_Index"].median()
    med_adoption = data["AI_Adoption_Pct"].median()

    fig, ax = plt.subplots(figsize=(10, 7))
    for region, grp in data.groupby("Region"):
        ax.scatter(grp["Digital_Skills_Index"], grp["AI_Adoption_Pct"],
                   label=region, color=REGION_PALETTE.get(region, "grey"),
                   s=100, alpha=0.85, edgecolors="white")
        for _, row in grp.iterrows():
            ax.annotate(row["Country_Code"],
                        (row["Digital_Skills_Index"], row["AI_Adoption_Pct"]),
                        textcoords="offset points", xytext=(4, 2), fontsize=8)

    ax.axvline(med_skills,   color="grey", ls="--", lw=1.2, label=f"Median skills ({med_skills:.1f})")
    ax.axhline(med_adoption, color="grey", ls=":",  lw=1.2, label=f"Median adoption ({med_adoption:.1f}%)")

    ax.text(med_skills + 1,   med_adoption + 1, "Leader",           fontsize=9, color="#27ae60")
    ax.text(med_skills + 1,   med_adoption - 4, "Skilled-Low-AI",   fontsize=9, color="#f39c12")
    ax.text(med_skills - 15,  med_adoption + 1, "Unskilled-High-AI",fontsize=9, color="#e67e22")
    ax.text(med_skills - 15,  med_adoption - 4, "Laggard",          fontsize=9, color="#e74c3c")

    ax.set_xlabel("Digital Skills Index")
    ax.set_ylabel("AI Adoption (%)")
    ax.set_title("Digital Divide Quadrant Analysis — Europe 2024")
    ax.legend(fontsize=9)
    save("chart6_digital_divide_quadrant")


# ── Chart 7: AI Readiness Score (Performance Index) ──────────────────────────

def chart_ai_readiness(df: pd.DataFrame) -> None:
    df = df.copy()
    df["inv_unemp_scaled"] = (1 / df["Unemployment_Rate"]) * 5
    df["AI_Readiness_Score"] = (
        df["Digital_Skills_Index"]     * 0.40 +
        df["inv_unemp_scaled"]         * 0.30 +
        df["ICT_Employment_pct"] * 10  * 0.15 +
        df["RD_Investment_pct_GDP"] * 10 * 0.15
    )

    data = (
        df[(df["Year"] == 2024) & (df["Company_Size"] == "Large")]
        .groupby(["Country_Code", "Region"])["AI_Readiness_Score"]
        .mean()
        .reset_index()
        .sort_values("AI_Readiness_Score", ascending=True)
    )

    colors = [REGION_PALETTE.get(r, "grey") for r in data["Region"]]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(data["Country_Code"], data["AI_Readiness_Score"],
            color=colors, edgecolor="none", height=0.7)
    ax.set_xlabel("AI Readiness Score (composite)")
    ax.set_title("Performance Index — Country AI Readiness (2024)")

    patches = [mpatches.Patch(color=v, label=k) for k, v in REGION_PALETTE.items()]
    ax.legend(handles=patches, fontsize=9)
    save("chart7_ai_readiness")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    df = load()
    print(f"  {len(df)} rows")

    print("\nGenerating charts:")
    chart_unemployment_vs_adoption(df)
    chart_skills_vs_adoption(df)
    chart_adoption_by_country(df)
    chart_adoption_by_size(df)
    chart_adoption_by_sector(df)
    chart_digital_divide_quadrant(df)
    chart_ai_readiness(df)

    print(f"\nAll charts saved to {CHART_DIR}/")


if __name__ == "__main__":
    main()
