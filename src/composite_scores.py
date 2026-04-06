"""
Composite scoring and quadrant logic for the EU AI adoption analysis.

Metrics
-------
1. AI Readiness Score — weighted multi-factor index (used in Tableau LOD chart)
2. Performance Index — ranking countries across all dimensions simultaneously
3. Digital Divide Quadrant — 2×2 grid based on skills vs adoption relative to EU median
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_data() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "sample_processed.csv")
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# 1. AI Readiness Score
# ---------------------------------------------------------------------------

def compute_ai_readiness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Weighted composite index:
        40% Digital Skills Index
        30% Inverse Unemployment (scaled ×5)
        15% ICT Employment (scaled ×10)
        15% R&D Investment % GDP (scaled ×10)

    Scaling factors align variables to a comparable numeric range.
    """
    df = df.copy()
    df["inv_unemp_scaled"] = (1 / df["Unemployment_Rate"]) * 5

    df["AI_Readiness_Score"] = (
        df["Digital_Skills_Index"]    * 0.40 +
        df["inv_unemp_scaled"]        * 0.30 +
        df["ICT_Employment_pct"] * 10 * 0.15 +
        df["RD_Investment_pct_GDP"] * 10 * 0.15
    ).round(2)

    return df


# ---------------------------------------------------------------------------
# 2. Performance Index (normalized, equal-weight)
# ---------------------------------------------------------------------------

PERF_FEATURES = [
    "AI_Adoption_Pct",
    "Digital_Skills_Index",
    "ICT_Employment_pct",
    "RD_Investment_pct_GDP",
]
PERF_INVERSE = ["Unemployment_Rate"]   # lower is better → invert


def compute_performance_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise each dimension to 0–100 and average.
    Mirrors the LOD expression in Tableau.
    """
    df = df.copy()
    country_avg = (
        df.groupby(["Country_Code", "Year"])[PERF_FEATURES + PERF_INVERSE]
        .mean()
        .reset_index()
    )

    scaler = MinMaxScaler(feature_range=(0, 100))
    cols_to_scale = PERF_FEATURES + PERF_INVERSE
    country_avg[cols_to_scale] = scaler.fit_transform(country_avg[cols_to_scale])

    # Invert so lower unemployment → higher score
    for col in PERF_INVERSE:
        country_avg[col] = 100 - country_avg[col]

    all_cols = PERF_FEATURES + PERF_INVERSE
    country_avg["Performance_Index"] = country_avg[all_cols].mean(axis=1).round(2)
    country_avg = country_avg.sort_values("Performance_Index", ascending=False)

    return country_avg[["Country_Code", "Year", "Performance_Index"] + all_cols]


# ---------------------------------------------------------------------------
# 3. Digital Divide Quadrant
# ---------------------------------------------------------------------------

def assign_quadrant(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify each country-year into a digital divide quadrant.

    Quadrants (relative to EU median):
        Leader          — high skills, high adoption
        Skilled-Low-AI  — high skills, low adoption (potential untapped)
        Unskilled-High-AI — low skills, high adoption (unsustainable?)
        Laggard         — low skills, low adoption
    """
    df = df.copy()
    country_avg = (
        df.groupby(["Country_Code", "Year"])[["Digital_Skills_Index", "AI_Adoption_Pct"]]
        .mean()
        .reset_index()
    )

    med_skills   = country_avg["Digital_Skills_Index"].median()
    med_adoption = country_avg["AI_Adoption_Pct"].median()

    country_avg["Quadrant"] = np.select(
        [
            (country_avg["Digital_Skills_Index"] >= med_skills) &
            (country_avg["AI_Adoption_Pct"]       >= med_adoption),

            (country_avg["Digital_Skills_Index"] >= med_skills) &
            (country_avg["AI_Adoption_Pct"]       <  med_adoption),

            (country_avg["Digital_Skills_Index"] <  med_skills) &
            (country_avg["AI_Adoption_Pct"]       >= med_adoption),
        ],
        ["Leader", "Skilled-Low-AI", "Unskilled-High-AI"],
        default="Laggard"
    )

    return country_avg[["Country_Code", "Year",
                         "Digital_Skills_Index", "AI_Adoption_Pct", "Quadrant"]]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = load_data()
    df = compute_ai_readiness(df)

    print("=== AI Readiness Score (top 10) ===")
    top = (
        df[df["Year"] == 2024]
        .groupby("Country_Code")[["AI_Readiness_Score", "AI_Adoption_Pct"]]
        .mean()
        .sort_values("AI_Readiness_Score", ascending=False)
        .head(10)
    )
    print(top.round(2).to_string())

    print("\n=== Performance Index (2024) ===")
    pi = compute_performance_index(df[df["Year"] == 2024])
    print(pi[["Country_Code", "Performance_Index"]].head(10).to_string(index=False))

    print("\n=== Digital Divide Quadrants (2024) ===")
    q = assign_quadrant(df[df["Year"] == 2024])
    print(q.sort_values("Quadrant").to_string(index=False))
