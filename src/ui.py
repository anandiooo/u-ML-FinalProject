import json
from pathlib import Path

import folium
import pandas as pd
import plotly.express as px
import streamlit as st

from src.modeling import predict_risk

FEATURE_LABELS = {
    "kepadatan_penduduk": "Kepadatan Penduduk (jiwa/km²)",
    "pct_tanpa_sanitasi": "% Tanpa Sanitasi Layak",
    "pct_tanpa_air_bersih": "% Tanpa Air Bersih",
    "volume_sampah_harian": "Volume Sampah Harian (ton)",
    "curah_hujan_mm": "Curah Hujan (mm)",
    "indeks_kualitas_air": "Indeks Kualitas Air",
    "jumlah_faskes_per_1000": "Faskes per 1.000 Penduduk",
    "risk_class": "Kelas Risiko",
    "kecamatan": "Kecamatan",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "periode": "Periode",
    "kondisi": "Kondisi",
}


def fl(name):
    """Get the display label for a feature name."""
    return FEATURE_LABELS.get(name, name)


def build_risk_map(df, config):
    geojson_path = config["paths"].get("geojson")
    center_lat = -6.2
    center_lon = 106.9

    risk_colors = config.get("risk_colors", {})
    risk_labels = config.get("risk_labels", {})
    risk_by_region = dict(zip(df.get("region_id", []), df.get("predicted_class", [])))

    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="cartodbpositron")

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
                popup=f"{row.get('kecamatan', row.get('region_name', 'Region'))} - {label}",
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
        _metric_card("Total Regions", f"{total_regions:,}", "Areas being monitored")
    with c2:
        _metric_card("Average Risk", f"{avg_risk:.2f}", "0 (Low) - 2 (High)")
    with c3:
        _metric_card("High Risk", f"{high_risk:,}", "Sanitation priority targets")

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

        # Interpretation
        macro_f1 = metrics.get('macro_f1', 0)
        perf_text = "Excellent" if macro_f1 > 0.8 else ("Good" if macro_f1 > 0.6 else "Needs Improvement")
        st.markdown(
            f"<div class='interp-box'><strong>Auto Interpretation:</strong> Overall model performance is at "
            f"<strong>{perf_text}</strong> level (Macro F1: {macro_f1:.2f}). This means the system is {'reliable enough' if macro_f1 > 0.6 else 'not reliable enough'} "
            f"to accurately identify which areas are most vulnerable to environment-based diseases.</div>",
            unsafe_allow_html=True
        )


def render_heatmap(config, df):
    st.markdown('<div class="section-heading">Spatial Risk Heatmap</div>', unsafe_allow_html=True)
    map_obj = build_risk_map(df, config)
    st.components.v1.html(map_obj.get_root().render(), height=520)

    # Interpretation
    risk_col = "predicted_label" if "predicted_label" in df.columns else "risk_class"

    # Check if this is the full dataframe or just simulation
    if len(df) > 1:
        # Check distribution for map interpretation
        counts = df[risk_col].value_counts()
        total = len(df)

        # Determine dominant risk
        if not counts.empty:
            dominant_risk = counts.idxmax()
            pct = (counts.max() / total) * 100

            # Use mapping to ensure we have string representation if it's numeric
            if isinstance(dominant_risk, (int, float)):
                risk_map = {0: "Risiko Rendah", 1: "Risiko Sedang", 2: "Risiko Tinggi"}
                dominant_str = risk_map.get(int(dominant_risk), str(dominant_risk))
            else:
                dominant_str = str(dominant_risk)

            st.markdown(
                f"<div class='interp-box'><strong>Auto Map Interpretation:</strong> Overall, the region is dominated by "
                f"<strong>{dominant_str}</strong> category which covers {pct:.1f}% of the area in the current dataset. "
                f"This distribution pattern can help health services focus budget and healthcare workforce allocation.</div>",
                unsafe_allow_html=True
            )


def render_simulation(config, df, artifacts):
    st.markdown('<div class="section-heading">What-If Analysis</div>', unsafe_allow_html=True)

    if artifacts is None:
        st.warning("Train the model first to enable simulation.")
        return None

    features = config["features"]
    baseline_inputs = df[features].median(numeric_only=True).to_dict()

    sim_inputs = {}
    for feature in features:
        mean_val = float(df[feature].mean()) if feature in df.columns else 0.0
        min_val = float(df[feature].min()) if feature in df.columns else -100.0
        max_val = float(df[feature].max()) if feature in df.columns else 10000.0
        sim_inputs[feature] = st.slider(
            fl(feature),
            min_value=min_val,
            max_value=max_val,
            value=mean_val,
            format="%.2f",
            key=f"sim_{feature}",
        )

    # ── Reactive prediction (no button needed) ──
    sample = pd.DataFrame([sim_inputs])
    result = predict_risk(sample, config, artifacts)

    # ── Delta interpretation ──
    from src.interpretation import generate_simulation_delta
    delta_text = generate_simulation_delta(baseline_inputs, sim_inputs, result, config)

    return {
        "result": result,
        "sim_inputs": sim_inputs,
        "baseline_inputs": baseline_inputs,
        "delta_text": delta_text
    }


def render_data(config, df):
    tab_raw, tab_dist, tab_target, tab_scatter, tab_corr = st.tabs([
        "Raw Data", "Feature Distribution", "Risk Analysis", "Scatter Plot", "Correlation"
    ])

    features = config["features"]
    target_col = "risk_class"
    risk_labels = config.get("risk_labels", {0: "Risiko Rendah", 1: "Risiko Sedang", 2: "Risiko Tinggi"})
    risk_colors = config.get("risk_colors", {0: "#10b981", 1: "#f59e0b", 2: "#ef4444"})

    df_plot = df.copy()
    if "predicted_label" in df_plot.columns:
        status_col = "predicted_label"
    else:
        status_col = "status_label"
        df_plot[status_col] = df_plot[target_col].map(risk_labels)

    color_map = {risk_labels[k]: v for k, v in risk_colors.items()}

    with tab_raw:
        st.caption(f"Showing total {len(df):,} data records")
        st.dataframe(df.rename(columns=FEATURE_LABELS), use_container_width=True, height=400)

    with tab_dist:
        col_ctrl, _ = st.columns([2, 3])
        feature = col_ctrl.selectbox("Feature to inspect:", features, format_func=fl, key="hist_feature")
        bins = col_ctrl.slider("Bin count:", 10, 60, 30, key="hist_bins")

        fig = px.histogram(
            df_plot, x=feature, nbins=bins,
            color=status_col, color_discrete_map=color_map, barmode="overlay",
            opacity=0.7,
            title=f"Distribution of {fl(feature)} by Risk Status",
            labels={feature: fl(feature)},
        )
        fig.update_layout(legend_title="Status", margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

        from src.interpretation import generate_eda_interpretation
        interp_text = generate_eda_interpretation(feature, df, target_col, config)
        if interp_text:
            st.markdown(f"<div class='interp-box'>{interp_text}</div>", unsafe_allow_html=True)

    with tab_target:
        col_ctrl2, _ = st.columns([2, 3])
        box_feature = col_ctrl2.selectbox("Numeric feature:", features, format_func=fl, key="box_feature")
        fig_box = px.box(
            df_plot, x=status_col, y=box_feature,
            color=status_col, color_discrete_map=color_map,
            title=f"{fl(box_feature)} vs Risk Status",
            labels={box_feature: fl(box_feature)},
            points="outliers",
        )
        fig_box.update_layout(showlegend=False, margin=dict(t=40, b=20))
        st.plotly_chart(fig_box, use_container_width=True)

    with tab_scatter:
        c1, c2 = st.columns(2)
        x_axis = c1.selectbox("X axis:", features, index=0, format_func=fl, key="sc_x")
        y_axis = c2.selectbox("Y axis:", features, index=min(1, len(features)-1), format_func=fl, key="sc_y")

        fig_sc = px.scatter(
            df_plot, x=x_axis, y=y_axis,
            color=status_col, color_discrete_map=color_map,
            opacity=0.6, size_max=6,
            title=f"{fl(x_axis)} vs {fl(y_axis)}",
            labels={x_axis: fl(x_axis), y_axis: fl(y_axis)},
        )
        fig_sc.update_layout(legend_title="Status", margin=dict(t=40, b=20))
        st.plotly_chart(fig_sc, use_container_width=True)

    with tab_corr:
        corr = df_plot[features + [target_col]].corr()
        corr_display = corr.rename(index=FEATURE_LABELS, columns=FEATURE_LABELS)
        fig_heat = px.imshow(
            corr_display, text_auto=".2f", color_continuous_scale="Blues",
            title="Pearson Correlation Matrix",
            zmin=-1, zmax=1,
        )
        fig_heat.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)

        from src.interpretation import generate_correlation_interpretation
        corr_text = generate_correlation_interpretation(df_plot, target_col, features, config)
        if corr_text:
            st.markdown(f"<div class='interp-box'>{corr_text}</div>", unsafe_allow_html=True)
