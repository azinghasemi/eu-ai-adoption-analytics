# EU AI Adoption Analytics

**Analysing the relationship between labour market sustainability, digital skills, and enterprise AI adoption across European economies using Eurostat data (2024–2025).**

---

## Research Questions

- Do countries with lower unemployment and higher digital skills show higher AI adoption?
- How does economic development (GDP, R&D investment) drive AI adoption at the national level?
- Do company size and industry sector explain within-country variation?
- Can a composite AI Readiness Index identify which structural factors matter most?

---

## Dataset

| Attribute | Detail |
|-----------|--------|
| Source | Eurostat (`isoc_eb_ai`, `isoc_eb_ain2`) + OECD + Oxford Insights |
| Coverage | 27 EU countries + Norway, Turkey, Western Balkans |
| Period | 2024–2025 |
| Records | 5,039 rows, 22 columns |
| Granularity | Country × Year × Company Size / Sector |

**Key variables:**

| Variable | Description |
|----------|-------------|
| `AI_Adoption_Pct` | Share of enterprises using AI (%) |
| `Unemployment_Rate` | National unemployment rate (%) |
| `Digital_Skills_Index` | Composite digital skills score (Eurostat DESI) |
| `GDP_per_capita` | GDP per capita (EUR, current prices) |
| `RD_Investment_pct_GDP` | R&D expenditure as % of GDP |
| `ICT_Employment_pct` | ICT specialists as % of employed |
| `Company_Size` | Large / Medium / Small enterprise |
| `NACE_Sector` | Industry classification (NACE Rev.2) |
| `Region` | Nordic / Western / Eastern / Southern Europe |

---

## Key Findings

| Hypothesis | Result |
|-----------|--------|
| H1: Lower unemployment → higher AI adoption | **Confirmed** — negative correlation, R²>0.80 |
| H2: Higher digital skills → higher AI adoption | **Confirmed** — positive correlation across all regions |
| H3: Labour market + skills explain regional gaps | **Confirmed** — clear North–South and East–West divide |
| H4: Nordic/Western countries lead AI adoption | **Confirmed** — Denmark, Finland, Sweden in top 5 |
| H5: Large enterprises adopt more than SMEs | **Confirmed** — gap widens with company size |
| H6: Technology sectors lead adoption | **Confirmed** — IT/ICT and scientific sectors highest |

**Composite AI Readiness** (weighted index):
```
AI_Readiness = (Digital_Skills × 0.40)
             + (1/Unemployment × 0.30)
             + (ICT_Employment × 0.15)
             + (R&D_pct_GDP × 0.15)
```
No single factor alone explains adoption — structural readiness requires all four.

---

## Project Structure

```
eu-ai-adoption-analytics/
├── data/
│   ├── data_dictionary.md        # Full column descriptions
│   └── sample_processed.csv      # 50-row sample of the final dataset
├── notebooks/
│   └── ai_adoption_analysis.ipynb  # Full EDA + composite index
├── src/
│   ├── data_preparation.py       # Load, clean, merge Eurostat sources
│   ├── composite_scores.py       # AI Readiness Index + quadrant logic
│   └── visualizations.py         # Matplotlib/Seaborn replication charts
├── tableau/
│   └── calculated_fields.md      # All Tableau LOD expressions + composite formulas
├── requirements.txt
└── README.md
```

---

## Reproducing the Analysis

```bash
pip install -r requirements.txt

# Step 1: prepare data
python src/data_preparation.py

# Step 2: compute composite scores
python src/composite_scores.py

# Step 3: generate charts
python src/visualizations.py

# Or run the full notebook end-to-end
jupyter lab notebooks/ai_adoption_analysis.ipynb
```

**Tableau workbook**: connect to `data/final_dataset.csv`; see `tableau/calculated_fields.md` for all custom expressions.

---

## Tools & Methods

| Task | Tool |
|------|------|
| Data cleaning & merging | Python (pandas) |
| Exploratory analysis | Matplotlib, Seaborn, SciPy |
| Interactive dashboards | Tableau Desktop |
| Advanced Tableau | LOD expressions, Reference lines, Composite calculated fields |
| Supplementary analysis | Excel (PivotTables, Combo charts, Slicer dashboards) |
| Correlation analysis | Pearson r, Spearman ρ |
