"""
Streamlit live demo — EU AI Adoption Analytics
Uses the sample dataset included in the repo. No external download required.

Run: streamlit run app.py
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_processed.csv")

REGION_COLORS = {
    "Nordic":  "#27ae60",
    "Western": "#2980b9",
    "Eastern": "#f39c12",
    "Southern": "#e74c3c",
}

QUADRANT_COLORS = {
    "Leader":             "#27ae60",
    "Skilled-Low-AI":     "#f39c12",
    "Unskilled-High-AI":  "#8e44ad",
    "Laggard":            "#e74c3c",
}

st.set_page_config(
    page_title="EU AI Adoption Analytics",
    page_icon="🇪🇺",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


df = load_data()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("EU AI Adoption Analytics")
st.markdown(
    "**Which EU countries are actually ready for AI — and why?**  \n"
    "Enterprise AI adoption across 30+ European economies · Eurostat 2024–2025 · "
    "Composite AI Readiness Index"
)

st.divider()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Filters")

    year = st.selectbox("Year", sorted(df["Year"].unique(), reverse=True))
    company_size = st.multiselect(
        "Company Size",
        options=df["Company_Size"].unique().tolist(),
        default=["Large"],
    )
    regions = st.multiselect(
        "Region",
        options=df["Region"].unique().tolist(),
        default=df["Region"].unique().tolist(),
    )
    sector = st.selectbox(
        "Sector (for sector view)",
        options=["All"] + sorted(df["NACE_Sector"].unique().tolist()),
    )

    st.divider()
    st.markdown("**AI Readiness Formula**")
    w_skills  = st.slider("Digital Skills weight", 0.0, 1.0, 0.40, 0.05)
    w_unemp   = st.slider("Employment weight",     0.0, 1.0, 0.30, 0.05)
    w_ict     = st.slider("ICT Employment weight", 0.0, 1.0, 0.15, 0.05)
    w_rd      = st.slider("R&D Investment weight", 0.0, 1.0, 0.15, 0.05)
    total_w   = w_skills + w_unemp + w_ict + w_rd
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"Weights sum to {total_w:.2f} — ideally should sum to 1.0")

# ---------------------------------------------------------------------------
# Filter data
# ---------------------------------------------------------------------------

mask = (
    (df["Year"] == year) &
    (df["Company_Size"].isin(company_size)) &
    (df["Region"].isin(regions))
)
if sector != "All":
    mask &= df["NACE_Sector"] == sector

df_f = df[mask].copy()

# Recompute readiness with slider weights
df_f["inv_unemp_scaled"] = (1 / df_f["Unemployment_Rate"]) * 5
df_f["AI_Readiness_Score"] = (
    df_f["Digital_Skills_Index"]    * w_skills +
    df_f["inv_unemp_scaled"]        * w_unemp  +
    df_f["ICT_Employment_pct"] * 10 * w_ict    +
    df_f["RD_Investment_pct_GDP"] * 10 * w_rd
).round(2)

country_avg = (
    df_f.groupby(["Country_Code", "Country_Name", "Region"])
    .agg(
        AI_Adoption_Pct    =("AI_Adoption_Pct", "mean"),
        AI_Readiness_Score =("AI_Readiness_Score", "mean"),
        Digital_Skills     =("Digital_Skills_Index", "mean"),
        Unemployment_Rate  =("Unemployment_Rate", "mean"),
        ICT_Employment     =("ICT_Employment_pct", "mean"),
        RD_Investment      =("RD_Investment_pct_GDP", "mean"),
        Quadrant           =("Quadrant", "first"),
    )
    .reset_index()
    .sort_values("AI_Readiness_Score", ascending=False)
)

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
col1.metric("Countries", len(country_avg))
col2.metric("Avg AI Adoption", f"{country_avg['AI_Adoption_Pct'].mean():.1f}%")
col3.metric("Top Country", country_avg.iloc[0]["Country_Name"] if not country_avg.empty else "—")
col4.metric("Leaders", int((country_avg["Quadrant"] == "Leader").sum()))

st.divider()

# ---------------------------------------------------------------------------
# Tab layout
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "AI Readiness Ranking", "Skills vs Adoption", "Regional Comparison", "Sector Breakdown"
])

# --- Tab 1: Ranking ---
with tab1:
    st.subheader(f"AI Readiness Ranking — {year}")
    st.caption("Composite index: Digital Skills (40%) + Employment (30%) + ICT Employment (15%) + R&D (15%)")

    if country_avg.empty:
        st.info("No data for selected filters.")
    else:
        fig = px.bar(
            country_avg,
            x="AI_Readiness_Score",
            y="Country_Name",
            color="Region",
            color_discrete_map=REGION_COLORS,
            orientation="h",
            text="AI_Readiness_Score",
            hover_data={"AI_Adoption_Pct": ":.1f", "Digital_Skills": ":.1f", "Unemployment_Rate": ":.1f"},
            labels={"AI_Readiness_Score": "AI Readiness Score", "Country_Name": ""},
        )
        fig.update_traces(textposition="outside", texttemplate="%{text:.1f}")
        fig.update_layout(
            height=max(400, len(country_avg) * 30),
            yaxis={"categoryorder": "total ascending"},
            legend_title="Region",
            margin=dict(l=0, r=60, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Scatter ---
with tab2:
    st.subheader("Digital Skills vs AI Adoption — Quadrant View")
    st.caption(
        "Each point = one country. Quadrants split at EU median. "
        "**Skilled-Low-AI** countries (top-left) have untapped AI potential."
    )

    if country_avg.empty:
        st.info("No data for selected filters.")
    else:
        med_skills   = country_avg["Digital_Skills"].median()
        med_adoption = country_avg["AI_Adoption_Pct"].median()

        fig = px.scatter(
            country_avg,
            x="Digital_Skills",
            y="AI_Adoption_Pct",
            color="Quadrant",
            color_discrete_map=QUADRANT_COLORS,
            text="Country_Code",
            size="AI_Readiness_Score",
            size_max=35,
            hover_data={"Country_Name": True, "AI_Readiness_Score": ":.1f", "Unemployment_Rate": ":.1f"},
            labels={
                "Digital_Skills":   "Digital Skills Index",
                "AI_Adoption_Pct":  "AI Adoption (%)",
            },
        )
        # Quadrant lines
        fig.add_hline(y=med_adoption, line_dash="dash", line_color="grey", opacity=0.5)
        fig.add_vline(x=med_skills,   line_dash="dash", line_color="grey", opacity=0.5)

        # Quadrant labels
        x_range = [country_avg["Digital_Skills"].min(), country_avg["Digital_Skills"].max()]
        y_range = [country_avg["AI_Adoption_Pct"].min(), country_avg["AI_Adoption_Pct"].max()]
        annotations = [
            ("Leader",           x_range[1] * 0.97, y_range[1] * 0.97),
            ("Skilled-Low-AI",   x_range[1] * 0.97, y_range[0] * 1.05),
            ("Unskilled-High-AI", x_range[0] * 1.02, y_range[1] * 0.97),
            ("Laggard",          x_range[0] * 1.02, y_range[0] * 1.05),
        ]
        for label, ax, ay in annotations:
            fig.add_annotation(
                x=ax, y=ay, text=f"<b>{label}</b>",
                showarrow=False, font=dict(size=11, color=QUADRANT_COLORS.get(label, "grey")),
                xanchor="right" if ax > med_skills else "left",
            )

        fig.update_traces(textposition="top center")
        fig.update_layout(height=520, margin=dict(l=0, r=0, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 3: Regional ---
with tab3:
    st.subheader("Regional Comparison")

    region_avg = (
        df_f.groupby("Region")
        .agg(
            AI_Adoption     =("AI_Adoption_Pct", "mean"),
            Digital_Skills  =("Digital_Skills_Index", "mean"),
            Unemployment    =("Unemployment_Rate", "mean"),
            RD_Investment   =("RD_Investment_pct_GDP", "mean"),
        )
        .reset_index()
        .round(2)
    )

    if region_avg.empty:
        st.info("No data for selected filters.")
    else:
        fig = go.Figure()
        metrics = {
            "AI_Adoption":    "AI Adoption (%)",
            "Digital_Skills": "Digital Skills Index",
            "RD_Investment":  "R&D Investment (% GDP)",
        }
        for col, label in metrics.items():
            fig.add_trace(go.Bar(
                name=label,
                x=region_avg["Region"],
                y=region_avg[col],
                text=region_avg[col],
                texttemplate="%{text:.1f}",
                textposition="outside",
            ))

        fig.update_layout(
            barmode="group",
            height=440,
            legend_title="Metric",
            xaxis_title="Region",
            yaxis_title="Value",
            margin=dict(l=0, r=0, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            region_avg.rename(columns={
                "Region": "Region",
                "AI_Adoption": "Avg AI Adoption %",
                "Digital_Skills": "Digital Skills Index",
                "Unemployment": "Unemployment Rate",
                "RD_Investment": "R&D % GDP",
            }),
            use_container_width=True,
            hide_index=True,
        )

# --- Tab 4: Sector ---
with tab4:
    st.subheader("AI Adoption by Sector")

    sector_avg = (
        df[
            (df["Year"] == year) &
            (df["Company_Size"].isin(company_size))
        ]
        .groupby("NACE_Sector")["AI_Adoption_Pct"]
        .mean()
        .reset_index()
        .sort_values("AI_Adoption_Pct", ascending=True)
        .rename(columns={"NACE_Sector": "Sector", "AI_Adoption_Pct": "Avg AI Adoption (%)"})
    )

    if sector_avg.empty:
        st.info("No data for selected filters.")
    else:
        fig = px.bar(
            sector_avg,
            x="Avg AI Adoption (%)",
            y="Sector",
            orientation="h",
            text="Avg AI Adoption (%)",
            color="Avg AI Adoption (%)",
            color_continuous_scale="Blues",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(
            height=420, showlegend=False,
            margin=dict(l=0, r=60, t=20, b=20),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("IT/ICT and Scientific sectors consistently lead. Construction and Trade lag across all regions.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "Data: Eurostat `isoc_eb_ai` · OECD · Oxford Insights AI Readiness Index · "
    "Part of the [EU AI Adoption Analytics](https://github.com/azinghasemi/eu-ai-adoption-analytics) project"
)
