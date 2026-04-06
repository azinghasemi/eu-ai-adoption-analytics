# Tableau Calculated Fields

All custom expressions used across the three dashboards.

---

## Dashboard 1 — Labour Market & Regional Patterns

### Labour Market Health Label
```
IF [Unemployment Rate] < 6 THEN "Stable"
ELSEIF [Unemployment Rate] < 10 THEN "Moderate"
ELSE "Fragile"
END
```

### Trend Label (for scatter annotation)
```
STR([Country Code]) + " (" + STR(ROUND([AI Adoption Pct], 1)) + "%)"
```

### Region Colour (used as discrete dimension for colour encoding)
`[Region]` — mapped manually to:
- Nordic → `#2c3e50`
- Western → `#2980b9`
- Southern → `#e74c3c`
- Eastern → `#f39c12`

---

## Dashboard 2 — Economic & Sectoral Analysis

### Development Level
```
IF [GDP Per Capita] >= 50000 THEN "High"
ELSEIF [GDP Per Capita] >= 25000 THEN "Medium"
ELSE "Low"
END
```

### Size Gap (Large minus Small)
```
{ FIXED [Country Code], [Year] :
    MAX(IF [Company Size] = "Large" THEN [AI Adoption Pct] END) }
-
{ FIXED [Country Code], [Year] :
    MAX(IF [Company Size] = "Small" THEN [AI Adoption Pct] END) }
```

### Sector Rank (within region)
Table calculation on `AVG([AI Adoption Pct])`:
- Compute using: `NACE Sector`
- Direction: descending
```
RANK(AVG([AI Adoption Pct]))
```

---

## Dashboard 3 — Advanced Analysis (LOD + Composite)

### Performance Index (LOD)
Normalised multi-factor country score, stable across filter changes.

```
(
  { FIXED [Country Code], [Year] : AVG([AI Adoption Pct]) }      / 100 * 0.25 +
  { FIXED [Country Code], [Year] : AVG([Digital Skills Index]) }  / 100 * 0.25 +
  (1 / { FIXED [Country Code], [Year] : AVG([Unemployment Rate]) }) * 5 / 100 * 0.25 +
  { FIXED [Country Code], [Year] : AVG([ICT Employment Pct]) }   / 10  * 0.25
) * 100
```

### AI Readiness Score (Composite — weighted)
```
[Digital Skills Index] * 0.40
+ (1 / [Unemployment Rate]) * 5 * 0.30
+ [ICT Employment Pct] * 10 * 0.15
+ [RD Investment Pct GDP] * 10 * 0.15
```

### Quadrant Label (Digital Divide)
Classifies countries relative to the EU median on both axes.

```
IF [Digital Skills Index] >= WINDOW_AVG(AVG([Digital Skills Index]))
   AND [AI Adoption Pct] >= WINDOW_AVG(AVG([AI Adoption Pct]))
THEN "Leader"

ELSEIF [Digital Skills Index] >= WINDOW_AVG(AVG([Digital Skills Index]))
   AND [AI Adoption Pct] < WINDOW_AVG(AVG([AI Adoption Pct]))
THEN "Skilled-Low-AI"

ELSEIF [Digital Skills Index] < WINDOW_AVG(AVG([Digital Skills Index]))
   AND [AI Adoption Pct] >= WINDOW_AVG(AVG([AI Adoption Pct]))
THEN "Unskilled-High-AI"

ELSE "Laggard"
END
```
*(Compute using: `Country Code`; direction: across table)*

### Inverse Unemployment (for scatter axis)
```
1 / [Unemployment Rate]
```

### R² Label (for scatter trend annotation)
```
"R² = " + STR(ROUND(CORR(AVG([Unemployment Rate]), AVG([AI Adoption Pct]))^2, 2))
```

---

## Reference Lines Used

| Chart | Reference Line | Value |
|-------|---------------|-------|
| Digital Divide scatter | X-axis median | `WINDOW_MEDIAN(AVG([Digital Skills Index]))` |
| Digital Divide scatter | Y-axis median | `WINDOW_MEDIAN(AVG([AI Adoption Pct]))` |
| Labour Market scatter | X threshold (Stable) | Constant = 6 |
| Labour Market scatter | X threshold (Fragile) | Constant = 10 |
| GDP scatter | EU average GDP | `WINDOW_AVG(AVG([GDP Per Capita]))` |

---

## Filters Applied Across Dashboards

| Filter | Scope | Default |
|--------|-------|---------|
| Year | All sheets | 2024 |
| Region | All sheets | All |
| Labour Market Health | Dashboard 1 | All |
| Company Size | Dashboard 2 | Large |
| NACE Sector | Dashboard 2 | All |
| Indicator Code | Dashboard 2 | All |
