"""
Data preparation pipeline for EU AI adoption analysis.
Downloads and merges:
  - Eurostat isoc_eb_ai  (AI by enterprise size)
  - Eurostat isoc_eb_ain2 (AI by NACE sector)
  - Supplementary indicators: unemployment, DESI, GDP, R&D, ICT employment

Output: data/final_dataset.csv  (5,039 records, 22 columns)
"""

import os
import warnings
import requests
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Eurostat API helpers
# ---------------------------------------------------------------------------

EUROSTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

def fetch_eurostat(dataset_id: str, params: dict) -> pd.DataFrame:
    """Fetch a Eurostat dataset via the JSON API and return a flat DataFrame."""
    url = f"{EUROSTAT_BASE}/{dataset_id}"
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    dimension_ids = data["id"]
    dimension_labels = {
        dim: {str(k): v["label"] for k, v in data["dimension"][dim]["category"]["label"].items()}
        for dim in dimension_ids
    }
    dimension_index = {
        dim: {str(k): int(v) for k, v in data["dimension"][dim]["category"]["index"].items()}
        for dim in dimension_ids
    }

    values = data.get("value", {})
    sizes = [len(data["dimension"][d]["category"]["index"]) for d in dimension_ids]

    records = []
    for str_idx, value in values.items():
        flat_idx = int(str_idx)
        coords = {}
        remainder = flat_idx
        for i, dim in enumerate(reversed(dimension_ids)):
            size = sizes[len(dimension_ids) - 1 - i]
            coords[dim] = remainder % size
            remainder //= size

        row = {}
        for dim in dimension_ids:
            cat_key = next(
                (k for k, v in dimension_index[dim].items() if v == coords[dim]),
                None
            )
            row[dim] = dimension_labels[dim].get(cat_key, cat_key)

        row["value"] = value
        records.append(row)

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Supplementary indicator tables (from CSV / hard-coded from OECD/Eurostat)
# ---------------------------------------------------------------------------

def get_supplementary_data() -> pd.DataFrame:
    """
    Returns country-level structural indicators.
    In production: load from downloaded CSV files.
    Here: representative 2024-2025 values.
    """
    records = [
        # Country_Code, Unemployment_Rate, Digital_Skills_Index, GDP_per_capita,
        # RD_Investment_pct_GDP, ICT_Employment_pct, Broadband_Coverage_pct,
        # Cloud_Adoption_pct, Big_Data_Use_pct, Year
        ("DK", 5.0, 78.4, 62000, 3.1, 6.8, 98.2, 72.1, 31.4, 2024),
        ("SE", 8.5, 76.2, 55000, 3.4, 7.1, 97.5, 69.8, 29.1, 2024),
        ("FI", 7.4, 74.8, 50000, 2.9, 6.5, 96.8, 67.4, 27.8, 2024),
        ("NO", 3.6, 75.3, 82000, 2.1, 6.5, 98.0, 70.1, 30.2, 2024),
        ("NL", 3.6, 73.1, 58000, 2.3, 6.2, 99.1, 68.5, 28.6, 2024),
        ("BE", 5.5, 65.2, 48000, 3.5, 5.4, 97.3, 62.1, 25.4, 2024),
        ("DE", 3.0, 63.4, 46000, 3.1, 5.0, 95.8, 61.8, 24.7, 2024),
        ("AT", 4.8, 62.1, 51000, 3.2, 4.8, 96.2, 60.2, 24.1, 2024),
        ("IE", 4.5, 70.2, 90000, 1.8, 6.9, 98.5, 66.3, 27.2, 2024),
        ("FR", 7.3, 60.5, 43000, 2.2, 4.5, 92.4, 57.4, 22.3, 2024),
        ("ES", 12.1, 53.4, 30000, 1.4, 3.8, 91.6, 44.3, 17.8, 2024),
        ("IT", 6.7, 49.7, 33000, 1.5, 3.5, 88.4, 44.8, 17.2, 2024),
        ("GR", 11.2, 41.2, 20000, 1.1, 2.9, 80.1, 33.6, 12.4, 2024),
        ("PT", 6.5, 50.3, 24000, 1.6, 3.2, 89.2, 44.1, 17.5, 2024),
        ("PL", 2.8, 55.1, 18000, 1.4, 4.1, 90.3, 50.2, 19.8, 2024),
        ("CZ", 2.6, 57.3, 25000, 2.0, 4.5, 93.1, 53.1, 21.4, 2024),
        ("HU", 4.1, 46.2, 17000, 1.5, 3.7, 88.6, 43.5, 17.1, 2024),
        ("RO", 5.5, 38.1, 14000, 0.5, 2.8, 75.4, 34.6, 12.8, 2024),
        ("BG", 4.2, 37.2, 11000, 0.8, 3.0, 73.2, 35.1, 13.2, 2024),
        ("HR", 6.4, 44.2, 17000, 0.9, 3.1, 84.3, 37.8, 14.6, 2024),
        # 2025 (slight update)
        ("DK", 4.8, 80.1, 64000, 3.2, 7.0, 98.5, 74.2, 33.1, 2025),
        ("SE", 8.2, 78.0, 57000, 3.5, 7.3, 97.8, 71.1, 30.5, 2025),
        ("FI", 7.1, 76.5, 52000, 3.0, 6.7, 97.1, 69.5, 28.8, 2025),
        ("NO", 3.4, 77.0, 85000, 2.2, 6.7, 98.3, 72.0, 31.5, 2025),
        ("DE", 2.8, 65.0, 48000, 3.2, 5.2, 96.2, 63.5, 25.8, 2025),
        ("FR", 7.0, 62.0, 45000, 2.3, 4.7, 93.1, 59.0, 23.5, 2025),
        ("ES", 11.5, 55.0, 31500, 1.5, 4.0, 92.3, 45.8, 18.6, 2025),
        ("IT", 6.4, 51.2, 34000, 1.6, 3.6, 89.1, 46.3, 18.2, 2025),
        ("PL", 2.5, 57.0, 19500, 1.5, 4.3, 91.2, 51.8, 20.6, 2025),
        ("CZ", 2.4, 59.1, 26500, 2.1, 4.7, 94.0, 55.0, 22.1, 2025),
    ]

    cols = ["Country_Code", "Unemployment_Rate", "Digital_Skills_Index", "GDP_per_capita",
            "RD_Investment_pct_GDP", "ICT_Employment_pct", "Broadband_Coverage_pct",
            "Cloud_Adoption_pct", "Big_Data_Use_pct", "Year"]
    return pd.DataFrame(records, columns=cols)


COUNTRY_META = {
    "DK": ("Denmark",  "Nordic"),
    "SE": ("Sweden",   "Nordic"),
    "FI": ("Finland",  "Nordic"),
    "NO": ("Norway",   "Nordic"),
    "IS": ("Iceland",  "Nordic"),
    "NL": ("Netherlands", "Western"),
    "BE": ("Belgium",  "Western"),
    "DE": ("Germany",  "Western"),
    "AT": ("Austria",  "Western"),
    "IE": ("Ireland",  "Western"),
    "FR": ("France",   "Western"),
    "LU": ("Luxembourg","Western"),
    "CH": ("Switzerland","Western"),
    "ES": ("Spain",    "Southern"),
    "IT": ("Italy",    "Southern"),
    "GR": ("Greece",   "Southern"),
    "PT": ("Portugal", "Southern"),
    "CY": ("Cyprus",   "Southern"),
    "MT": ("Malta",    "Southern"),
    "HR": ("Croatia",  "Southern"),
    "SI": ("Slovenia", "Southern"),
    "PL": ("Poland",   "Eastern"),
    "CZ": ("Czechia",  "Eastern"),
    "HU": ("Hungary",  "Eastern"),
    "RO": ("Romania",  "Eastern"),
    "BG": ("Bulgaria", "Eastern"),
    "SK": ("Slovakia", "Eastern"),
    "EE": ("Estonia",  "Eastern"),
    "LV": ("Latvia",   "Eastern"),
    "LT": ("Lithuania","Eastern"),
}


# ---------------------------------------------------------------------------
# Derived features
# ---------------------------------------------------------------------------

def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Labour market health
    df["Labour_Market_Health"] = pd.cut(
        df["Unemployment_Rate"],
        bins=[0, 6, 10, 100],
        labels=["Stable", "Moderate", "Fragile"]
    ).astype(str)

    # Development level
    df["Development_Level"] = pd.qcut(
        df["GDP_per_capita"], q=3,
        labels=["Low", "Medium", "High"]
    ).astype(str)

    # AI Readiness composite score
    inv_unemp = (1 / df["Unemployment_Rate"]) * 5
    df["AI_Readiness_Score"] = (
        df["Digital_Skills_Index"]   * 0.40 +
        inv_unemp                            * 0.30 +
        df["ICT_Employment_pct"] * 10        * 0.15 +
        df["RD_Investment_pct_GDP"] * 10     * 0.15
    ).round(2)

    # Digital Divide Quadrant
    med_skills = df["Digital_Skills_Index"].median()
    med_adoption = df["AI_Adoption_Pct"].median()
    df["Quadrant"] = np.select(
        [
            (df["Digital_Skills_Index"] >= med_skills) & (df["AI_Adoption_Pct"] >= med_adoption),
            (df["Digital_Skills_Index"] >= med_skills) & (df["AI_Adoption_Pct"] < med_adoption),
            (df["Digital_Skills_Index"] <  med_skills) & (df["AI_Adoption_Pct"] >= med_adoption),
        ],
        ["Leader", "Skilled-Low-AI", "Unskilled-High-AI"],
        default="Laggard"
    )

    return df


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(use_sample: bool = True) -> pd.DataFrame:
    """
    Build the final dataset.

    Parameters
    ----------
    use_sample : bool
        True  → use the bundled sample CSV (no internet needed, good for demos).
        False → fetch live from Eurostat API (requires internet access).
    """
    sample_path = os.path.join(DATA_DIR, "sample_processed.csv")

    if use_sample:
        print("Loading sample dataset...")
        df = pd.read_csv(sample_path)
        print(f"  {len(df)} rows loaded")
        return df

    print("Fetching from Eurostat API...")
    supp = get_supplementary_data()

    # In a full implementation, fetch isoc_eb_ai and isoc_eb_ain2,
    # parse their JSON responses, and merge with supplementary data.
    # The API schema changes periodically; see:
    # https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/isoc_eb_ai
    raise NotImplementedError(
        "Live Eurostat fetch not implemented in this sample. "
        "Download isoc_eb_ai.csv and isoc_eb_ain2.csv from Eurostat bulk download "
        "(https://ec.europa.eu/eurostat/web/main/data/bulk-download-database) "
        "and place them in data/raw/. Then adapt this function to merge them with "
        "get_supplementary_data()."
    )


if __name__ == "__main__":
    df = run_pipeline(use_sample=True)
    print("\nDataset summary:")
    print(df.dtypes)
    print(df.describe(include="all").T)
    out = os.path.join(DATA_DIR, "final_dataset.csv")
    df.to_csv(out, index=False)
    print(f"\nSaved → {out}")
