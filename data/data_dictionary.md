# Data Dictionary

## Primary Sources

| Dataset ID | Source | Description |
|------------|--------|-------------|
| `isoc_eb_ai` | Eurostat | AI adoption by enterprise size class |
| `isoc_eb_ain2` | Eurostat | AI adoption by NACE Rev.2 sector |
| DESI 2024 | European Commission | Digital Economy and Society Index |
| OECD Stats | OECD | R&D expenditure, ICT employment |
| World Bank WDI | World Bank | GDP per capita, unemployment |

## Final Dataset Columns (5,039 records, 22 columns)

| Column | Type | Range / Values | Description |
|--------|------|---------------|-------------|
| `Country_Code` | str | ISO 3166-1 alpha-2 | Country identifier (e.g. DE, SE, PL) |
| `Country_Name` | str | — | Full country name |
| `Region` | str | Nordic / Western / Eastern / Southern | European sub-region grouping |
| `Year` | int | 2024, 2025 | Reference year |
| `Company_Size` | str | Large / Medium / Small / All | Enterprise size classification |
| `NACE_Code` | str | A–S | NACE Rev.2 sector code |
| `NACE_Sector` | str | — | Sector name (e.g. IT, Manufacturing) |
| `AI_Adoption_Pct` | float | 0–100 | % of enterprises using at least one AI technology |
| `Unemployment_Rate` | float | 2–20 | Annual national unemployment rate (%) |
| `Labour_Market_Health` | str | Stable / Moderate / Fragile | Derived: <6% Stable, 6–10% Moderate, >10% Fragile |
| `Digital_Skills_Index` | float | 0–100 | DESI Digital Skills dimension score |
| `DESI_Overall` | float | 0–100 | Overall DESI score |
| `GDP_per_capita` | float | — | GDP per capita (EUR, current prices) |
| `Development_Level` | str | High / Medium / Low | Derived from GDP per capita tertiles |
| `RD_Investment_pct_GDP` | float | 0–5 | Gross domestic R&D expenditure as % of GDP |
| `ICT_Employment_pct` | float | 0–15 | ICT specialists as % of total employed |
| `Broadband_Coverage_pct` | float | 0–100 | Household broadband coverage (%) |
| `Cloud_Adoption_pct` | float | 0–100 | % of enterprises using cloud services |
| `Big_Data_Use_pct` | float | 0–100 | % of enterprises using big data analytics |
| `Indicator_Code` | str | — | Original Eurostat indicator identifier |
| `AI_Readiness_Score` | float | 0–100 | Composite: see formula below |
| `Quadrant` | str | Leader / Skilled-Low-AI / Unskilled-High-AI / Laggard | Digital Divide quadrant label |

## Derived Metrics

### AI Readiness Score

Composite index measuring structural readiness for AI adoption.

```
AI_Readiness = (Digital_Skills_Index * 0.40)
             + ((1 / Unemployment_Rate) * 5 * 0.30)
             + (ICT_Employment_pct * 10 * 0.15)
             + (RD_Investment_pct_GDP * 10 * 0.15)
```

Weights: Digital Skills 40%, Inverse Unemployment 30%, ICT Employment 15%, R&D Spending 15%.
Scaling factors (5 and 10) align variables to a common numeric range before weighting.

### Digital Divide Quadrant

Derived by comparing each country to the EU median on two dimensions:

| Quadrant | Digital Skills | AI Adoption |
|----------|---------------|-------------|
| Leader | ≥ Median | ≥ Median |
| Skilled-Low-AI | ≥ Median | < Median |
| Unskilled-High-AI | < Median | ≥ Median |
| Laggard | < Median | < Median |

### Labour Market Health

| Label | Unemployment Rate |
|-------|------------------|
| Stable | < 6% |
| Moderate | 6% – 10% |
| Fragile | > 10% |

## Regional Groupings

| Region | Countries |
|--------|----------|
| Nordic | Denmark, Finland, Norway, Sweden, Iceland |
| Western | Germany, France, Netherlands, Belgium, Austria, Ireland, Luxembourg, Switzerland |
| Southern | Italy, Spain, Portugal, Greece, Cyprus, Malta, Croatia, Slovenia |
| Eastern | Poland, Czech Republic, Hungary, Romania, Bulgaria, Slovakia, Baltic states |
| Other | Turkey, Western Balkans |
