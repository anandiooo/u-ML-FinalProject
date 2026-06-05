import json
from pathlib import Path

import folium
import pandas as pd
import plotly.express as px
import streamlit as st

from src.modeling import predict_risk


def build_risk_map(df, config):
    geojson_path = config["paths"].get("geojson")
    center_lat = -6.1
    center_lon = 106.9

    risk_colors = config.get("risk_colors", {})
    risk_labels = config.get("risk_labels", {})
    risk_by_region = dict(zip(df.get("region_id", []), df.get("predicted_class", [])))

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="cartodbpositron")

    if geojson_path and Path(geojson_path).exists():
        with Path(geojson_path).open("r", encoding="utf-8") as f:
            geojson = json.load(f)

        def style_function(feature):
            region_id = feature.get("properties", {}).get("region_id")
            cls = risk_by_region.get(region_id)
            fill = risk_colors.get(cls, "#94a3b8")
            return {
                "fillColor": fill,
                "color": "#1d293d",
                "weight": 1,
                "fillOpacity": 0.7,
            }

        tooltip = folium.GeoJsonTooltip(fields=["region_id"], aliases=["Region ID:"])
        folium.GeoJson(geojson, style_function=style_function, tooltip=tooltip).add_to(m)
    else:
        for _, row in df.iterrows():
            lat = row.get("latitude", center_lat)
            lon = row.get("longitude", center_lon)
            if pd.isna(lat) or pd.isna(lon):
                continue

            cls = row.get("predicted_class")
            color = risk_colors.get(cls, "#94a3b8")
            label = risk_labels.get(cls, "Unknown")
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                popup=f"{row.get('region_name', 'Region')} - {label}",
            ).add_to(m)

    return m


def _metric_card(label, value, sub=""):
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='label'>{label}</div>"
        f"<div class='value'>{value}</div>"
        f"<div class='sub'>{sub}</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_dashboard(config, df, metrics=None):
    st.markdown('<div class="section-heading">Regional Summary</div>', unsafe_allow_html=True)

    total_regions = len(df)
    avg_risk = df.get("predicted_class", df.get("risk_class")).mean()
    high_risk = (df.get("predicted_class", df.get("risk_class")) == 2).sum()

    c1, c2, c3 = st.columns(3)
    with c1:
        _metric_card("Regions", f"{total_regions:,}", "tracked areas")
    with c2:
        _metric_card("Avg Risk", f"{avg_risk:.2f}", "0 low - 2 high")
    with c3:
        _metric_card("High Risk", f"{high_risk:,}", "priority targets")

    st.markdown('<div class="section-heading">Risk Distribution</div>', unsafe_allow_html=True)
    risk_col = "predicted_label" if "predicted_label" in df.columns else "risk_class"
    risk_counts = df[risk_col].value_counts().reset_index()
    risk_counts.columns = ["Risk", "Count"]
    fig = px.bar(risk_counts, x="Risk", y="Count", color="Count", color_continuous_scale=["#1d293d", "#615fff"])
    fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    if metrics:
        st.markdown('<div class="section-heading">Model Performance</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Macro F1", f"{metrics.get('macro_f1', 0):.3f}")
        c2.metric("Precision", f"{metrics.get('macro_precision', 0):.3f}")
        c3.metric("Recall", f"{metrics.get('macro_recall', 0):.3f}")
        c4.metric("Micro F1", f"{metrics.get('micro_f1', 0):.3f}")


def render_heatmap(config, df):
    st.markdown('<div class="section-heading">Spatial Risk Heatmap</div>', unsafe_allow_html=True)
    map_obj = build_risk_map(df, config)
    st.components.v1.html(map_obj.get_root().render(), height=520)


def render_simulation(config, df, artifacts):
    st.markdown('<div class="section-heading">Scenario Simulator</div>', unsafe_allow_html=True)

    if artifacts is None:
        st.warning("Train or load models to enable simulations.")
        return

    features = config["features"]
    defaults = df[features].median(numeric_only=True)

    sim_inputs = {}
    for feature in features:
        mean_val = float(df[feature].mean()) if feature in df.columns else 0.0
        min_val = float(df[feature].min()) if feature in df.columns else -100.0
        max_val = float(df[feature].max()) if feature in df.columns else 10000.0
        sim_inputs[feature] = st.slider(feature, min_value=min_val, max_value=max_val, value=mean_val, format="%.2f")

    if st.button("Run Simulation", type="primary"):
        sample = pd.DataFrame([sim_inputs])
        result = predict_risk(sample, config, artifacts)
        label = result.loc[0, "predicted_label"]
        prob = result.loc[0, "predicted_probability"]

        st.markdown(
            f"<div class='interp-box'><strong>Predicted Risk:</strong> {label}<br>"
            f"Confidence: {prob:.2f}</div>",
            unsafe_allow_html=True,
        )


def render_data(config, df):
    st.markdown('<div class="section-heading">Exploratory Data Analysis</div>', unsafe_allow_html=True)

    tab_raw, tab_dist, tab_target, tab_scatter, tab_corr = st.tabs([
        "Raw Data", "Distributions", "Target Analysis", "Scatter", "Correlations"
    ])

    features = config["features"]
    target_col = "risk_class"
    risk_labels = config.get("risk_labels", {0: "Baik", 1: "Ringan", 2: "Sedang", 3: "Berat"})
    risk_colors = config.get("risk_colors", {0: "#10b981", 1: "#f59e0b", 2: "#ef4444", 3: "#7f1d1d"})

    df_plot = df.copy()
    if "predicted_label" in df_plot.columns:
        status_col = "predicted_label"
    else:
        status_col = "status_label"
        df_plot[status_col] = df_plot[target_col].map(risk_labels)

    color_map = {risk_labels[k]: v for k, v in risk_colors.items()}

    with tab_raw:
        st.caption(f"Showing all {len(df):,} records")
        st.dataframe(df, use_container_width=True, height=400)

    with tab_dist:
        col_ctrl, _ = st.columns([2, 3])
        feature = col_ctrl.selectbox("Feature to inspect:", features, key="hist_feature")
        bins = col_ctrl.slider("Bin count:", 10, 60, 30, key="hist_bins")

        fig = px.histogram(
            df_plot, x=feature, nbins=bins,
            color=status_col, color_discrete_map=color_map, barmode="overlay",
            opacity=0.7,
            title=f"Distribution of {feature} by Risk Status"
        )
        fig.update_layout(legend_title="Status", margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with tab_target:
        col_ctrl2, _ = st.columns([2, 3])
        box_feature = col_ctrl2.selectbox("Numeric feature:", features, key="box_feature")
        fig_box = px.box(
            df_plot, x=status_col, y=box_feature,
            color=status_col, color_discrete_map=color_map,
            title=f"{box_feature} vs Risk Status",
            points="outliers",
        )
        fig_box.update_layout(showlegend=False, margin=dict(t=40, b=20))
        st.plotly_chart(fig_box, use_container_width=True)

    with tab_scatter:
        c1, c2 = st.columns(2)
        x_axis = c1.selectbox("X axis:", features, index=0, key="sc_x")
        y_axis = c2.selectbox("Y axis:", features, index=min(1, len(features)-1), key="sc_y")

        fig_sc = px.scatter(
            df_plot, x=x_axis, y=y_axis,
            color=status_col, color_discrete_map=color_map,
            opacity=0.6, size_max=6,
            title=f"{x_axis} vs {y_axis}"
        )
        fig_sc.update_layout(legend_title="Status", margin=dict(t=40, b=20))
        st.plotly_chart(fig_sc, use_container_width=True)

    with tab_corr:
        corr = df_plot[features + [target_col]].corr()
        fig_heat = px.imshow(
            corr, text_auto=".2f", color_continuous_scale="Blues",
            title="Pearson Correlation Matrix",
            zmin=-1, zmax=1,
        )
        fig_heat.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)
