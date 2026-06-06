import sys
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SaniSight",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 300; }

:root {
    --primary:   #615fff;
    --surface:   #1d293d;
    --surface-2: #0f172b;
    --border:    #314158;
    --text-main: #e2e8f0;
    --text-muted:#94a3b8;
    --radius:    6px;
}

:root, [data-theme="light"], [data-theme="dark"] {
    --primary-color: var(--primary) !important;
    --background-color: var(--surface-2) !important;
    --secondary-background-color: var(--surface) !important;
    --text-color: var(--text-main) !important;
}

[data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
    --st-color-background: var(--surface-2) !important;
    --st-color-secondary-background: var(--surface) !important;
    --st-color-text: var(--text-main) !important;
    --st-color-primary: var(--primary) !important;
}

body { background-color: var(--surface-2) !important; color: var(--text-main) !important; }
[data-testid="stAppViewContainer"] { background-color: var(--surface-2) !important; }

section[data-testid="stSidebar"] {
    background-color: var(--surface-2) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebarContent"] {
    display: flex;
    flex-direction: column;
}
section[data-testid="stSidebar"] * { color: var(--text-main) !important; }
.sidebar-info {
    display: flex; align-items: center;
    padding: 0px 8px; border-radius: 6px;
    font-size: 1rem; color: var(--text-main);
}

[data-testid="stHeader"] { height: 0px !important; background: transparent !important; }
.main .block-container { padding: 1rem 2rem !important; max-width: 1280px; background-color: var(--surface-2); }

.page-header { margin-bottom: 1.5rem; }
.page-header h1 {
    font-size: 2.8rem; font-weight: 400;
    color: var(--text-main); margin: 0;
    letter-spacing: -0.6px;
}

.section-heading {
    font-size: 1.15rem; font-weight: 400;
    color: var(--text-muted); text-transform: uppercase;
    letter-spacing: .06em; margin: 1.5rem 0 .75rem;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.3rem;
    transition: all 0.2s ease-in-out;
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: var(--primary);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}
.metric-card .label {
    font-size: .85rem; font-weight: 400;
    text-transform: uppercase; letter-spacing: .07em;
    color: var(--text-muted); margin-bottom: .3rem;
}
.metric-card .value {
    font-size: 1.85rem; font-weight: 400;
    color: var(--text-main); letter-spacing: -1px;
}
.metric-card .sub {
    font-size: .85rem; color: var(--text-muted); margin-top: .2rem;
}

.interp-box, .ok-box, .warn-box, .risk-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: .9rem 1.2rem; margin-top: .75rem;
    font-size: 0.95rem; color: var(--text-main); line-height: 1.6;
}
.interp-box { border-left: 4px solid var(--primary); }
.ok-box { border-left: 4px solid #10b981; }
.warn-box { border-left: 4px solid #f59e0b; }
.risk-box { border-left: 4px solid #ef4444; }

.interp-box strong { color: var(--primary); }
.ok-box strong { color: #10b981; }
.warn-box strong { color: #f59e0b; }
.risk-box strong { color: #ef4444; }

.stNumberInput > div > div > input,
.stTextInput  > div > div > input,
.stSelectbox [data-baseweb="select"] {
    border-radius: 8px !important;
    background-color: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text-main) !important;
}
.stSelectbox > div > div > div { border: none !important; }
.stSlider .stSlider { accent-color: var(--primary); }

div.stButton > button[kind="primary"] {
    background: var(--primary) !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    transition: filter 0.2s;
}
div.stButton > button[kind="primary"]:hover { filter: brightness(1.1); }

div.stButton > button:not([kind="primary"]) {
    border-radius: 8px !important;
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    transition: border-color 0.2s, color 0.2s;
}
div.stButton > button:not([kind="primary"]):hover {
    border-color: var(--primary) !important;
    color: var(--primary) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px; border-bottom: 2px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0 !important;
    font-weight: 400 !important; font-size: 1rem !important;
    background-color: transparent !important;
    color: var(--text-muted) !important;
    padding: 10px 16px !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary) !important;
}

[data-testid="stTable"], [data-testid="stDataFrame"] {
    background-color: var(--surface) !important;
}
</style>
""", unsafe_allow_html=True)

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.data import load_dataset
from src.modeling import (
    load_artifacts,
    load_metrics,
    predict_risk,
    run_training_pipeline,
)
from src.ui import (
    render_dashboard,
    render_data,
    render_heatmap,
    render_simulation,
)

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


def ibox(text, kind="info"):
    cls = {"info": "interp-box", "warn": "warn-box", "ok": "ok-box", "risk": "risk-box"}[kind]
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def page_header(title, subtitle=""):
    st.markdown(
        f'<div class="page-header">'
        f'<div><h1>{title}</h1>'
        + (f'<p style="margin:0;color:var(--text-muted);font-size:1.05rem">{subtitle}</p>' if subtitle else "")
        + "</div></div>",
        unsafe_allow_html=True,
    )


@st.cache_data
def load_dataset_cached(config):
    return load_dataset(config)


@st.cache_resource
def load_artifacts_cached(config):
    return load_artifacts(config=config)


@st.cache_data
def load_metrics_cached(config):
    return load_metrics(config=config)


config = load_config()
artifacts = load_artifacts_cached(config)
metrics = load_metrics_cached(config)

df = load_dataset_cached(config)
if artifacts:
    preds = predict_risk(df, config, artifacts)
    df_view = pd.concat([df.reset_index(drop=True), preds], axis=1)
else:
    df_view = df.copy()

def page_home():
    page_header("Spatial-Based Health Risk Prediction System", "Sistem Pendukung Keputusan Berbasis Tata Ruang")
    
    st.markdown('<div class="section-heading">Problem Statement</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.05rem; line-height: 1.6; color: var(--text-main); margin-bottom: 2rem;">
        Merujuk pada target RPJMN 2025–2029 dan pilar Smart City, Perencanaan infrastruktur kesehatan dan tata kota, khususnya di kawasan aglomerasi padat penduduk seperti area Jakarta dan Bekasi, seringkali masih berjalan secara terpisah dan reaktif. Data kondisi lingkungan, seperti kualitas sanitasi, jarang dihubungkan secara langsung dengan data penyebaran penyakit dasar seperti ISPA atau diare. Akibatnya, tindakan penanganan biasanya baru diturunkan setelah lonjakan kasus penyakit terjadi di suatu kecamatan. Proyek ini mengusulkan sebuah Sistem Pendukung Keputusan (Decision Support System) berbasis data keruangan. Sistem ini dirancang untuk memprediksi tingkat risiko kesehatan di suatu wilayah secara proaktif.
    </div>
    """, unsafe_allow_html=True)
    
    render_dashboard(config, df_view, metrics)


def page_eda():
    page_header("Eksplorasi Data", "Tinjauan Kualitas Lingkungan & Kesehatan")
    render_data(config, df_view)


def page_preprocessing():
    page_header("Preprocessing", "Konfigurasi dan verifikasi pipeline data")

    features = config["features"]
    target = config["target"]

    # ── Pipeline Configuration ──
    st.markdown('<div class="section-heading">Pipeline Configuration</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        missing_strategy = st.selectbox(
            "Missing Value Strategy",
            ["Median", "Mean", "Drop Rows"],
            index=0,
            help="How to handle missing values in numeric features.",
        )
        drop_duplicates = st.checkbox("Drop Duplicate Rows", value=True)

    with c2:
        scaling_method = st.selectbox(
            "Feature Scaling",
            ["StandardScaler", "MinMaxScaler", "None"],
            index=0,
            help="Scaling method applied to numeric features before training.",
        )
        outlier_method = st.selectbox(
            "Outlier Handling",
            ["None", "Clip (IQR)", "Remove"],
            index=0,
            help="Strategy for outlier treatment on numeric columns.",
        )

    with c3:
        selected_features = st.multiselect(
            "Features to Include",
            features,
            default=features,
            format_func=fl,
            help="Select which features to keep for modeling.",
        )

    st.session_state["preprocess_cfg"] = {
        "missing_strategy": missing_strategy,
        "scaling_method": scaling_method,
        "outlier_method": outlier_method,
        "drop_duplicates": drop_duplicates,
        "selected_features": selected_features,
    }

    st.divider()

    # ── Apply preview transformations ──
    df_preview = df.copy()

    # Drop duplicates
    orig_len = len(df_preview)
    if drop_duplicates:
        df_preview = df_preview.drop_duplicates()

    # Handle missing values
    num_cols = [c for c in selected_features if c in df_preview.columns]
    if missing_strategy == "Median":
        df_preview[num_cols] = df_preview[num_cols].fillna(df_preview[num_cols].median())
    elif missing_strategy == "Mean":
        df_preview[num_cols] = df_preview[num_cols].fillna(df_preview[num_cols].mean())
    elif missing_strategy == "Drop Rows":
        df_preview = df_preview.dropna(subset=num_cols)

    # Outlier handling
    if outlier_method == "Clip (IQR)":
        for col in num_cols:
            q1 = df_preview[col].quantile(0.25)
            q3 = df_preview[col].quantile(0.75)
            iqr = q3 - q1
            df_preview[col] = df_preview[col].clip(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
    elif outlier_method == "Remove":
        for col in num_cols:
            q1 = df_preview[col].quantile(0.25)
            q3 = df_preview[col].quantile(0.75)
            iqr = q3 - q1
            mask = (df_preview[col] >= q1 - 1.5 * iqr) & (df_preview[col] <= q3 + 1.5 * iqr)
            df_preview = df_preview[mask]

    # ── Live Quality Audit ──
    st.markdown('<div class="section-heading">Live Quality Audit</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Dataset Rows", f"{len(df_preview):,}", delta=int(len(df_preview) - orig_len))
    m2.metric("Selected Features", f"{len(selected_features)}", delta=int(len(selected_features) - len(features)))
    missing_clean = df_preview[num_cols].isnull().sum().sum() if num_cols else 0
    missing_orig = df[num_cols].isnull().sum().sum() if num_cols else 0
    m3.metric("Missing Cells", f"{missing_clean:,}", delta=int(-(missing_orig - missing_clean)) if missing_orig > 0 else 0)

    if target in df_preview.columns:
        counts = df_preview[target].value_counts()
        risk_labels = config.get("risk_labels", {})
        dist_data = []
        for cls_id in sorted(counts.index):
            label = risk_labels.get(cls_id, risk_labels.get(str(cls_id), str(cls_id)))
            dist_data.append({"Kelas": label, "Jumlah": counts[cls_id], "Persentase": counts[cls_id] / len(df_preview)})
        m4.metric("Total Classes", f"{len(counts)}")
    else:
        m4.metric("Total Classes", "N/A")

    # Class distribution table
    if target in df_preview.columns and dist_data:
        st.markdown('<div class="section-heading">Class Distribution</div>', unsafe_allow_html=True)
        dist_df = pd.DataFrame(dist_data)
        st.dataframe(
            dist_df.style.format({"Persentase": "{:.1%}"}),
            hide_index=True,
            use_container_width=True,
        )

    # Active pipeline summary
    st.markdown('<div class="section-heading">Active Pipeline Summary</div>', unsafe_allow_html=True)
    pipe_items = [
        f"Missing Values → **{missing_strategy}**",
        f"Scaling → **{scaling_method}**",
        f"Outliers → **{outlier_method}**",
        f"Drop Duplicates → **{'Yes' if drop_duplicates else 'No'}**",
        f"Features → **{len(selected_features)}** of {len(features)}",
    ]
    for item in pipe_items:
        st.markdown(f"- {item}")

    # Data Preview
    st.markdown('<div class="section-heading">Data Preview (Processed)</div>', unsafe_allow_html=True)
    st.dataframe(df_preview.rename(columns=FEATURE_LABELS), use_container_width=True)
    st.caption(f"Showing {len(df_preview):,} total records.")

    # Column Statistics
    st.markdown('<div class="section-heading">Column Statistics</div>', unsafe_allow_html=True)
    stats_df = df_preview[num_cols].describe() if num_cols else df_preview.describe()
    st.dataframe(stats_df.rename(columns=FEATURE_LABELS), use_container_width=True)


def page_train_eval():
    page_header("Train & Evaluate", "Latih model dan evaluasi performa")

    tab_train, tab_eval = st.tabs(["Train", "Evaluate"])

    with tab_train:
        c_left, c_right = st.columns([1, 1], gap="large")

        with c_left:
            st.markdown('<div class="section-heading">Model Selection</div>', unsafe_allow_html=True)
            model_choice = st.selectbox(
                "Algorithm",
                ["XGBoost (Primary)", "Logistic Regression (Baseline)"],
                index=0,
                help="Pick the machine learning algorithm to train.",
            )

            with st.expander("Hyperparameters", expanded=True):
                st.caption("Adjusting these tunes the bias–variance tradeoff.")
                train_cfg = config.get("training", {})

                if model_choice.startswith("XGBoost"):
                    xgb_cfg = train_cfg.get("xgboost", {})
                    n_est = st.slider("n_estimators", 50, 500, int(xgb_cfg.get("n_estimators", 250)), 50)
                    lr = st.slider("learning_rate", 0.01, 0.50, float(xgb_cfg.get("learning_rate", 0.08)), 0.01)
                    depth = st.slider("max_depth", 2, 12, int(xgb_cfg.get("max_depth", 4)), 1)
                    subsample = st.slider("subsample", 0.5, 1.0, float(xgb_cfg.get("subsample", 0.9)), 0.05)
                    colsample = st.slider("colsample_bytree", 0.5, 1.0, float(xgb_cfg.get("colsample_bytree", 0.9)), 0.05)
                    reg_lambda = st.slider("reg_lambda", 0.0, 10.0, float(xgb_cfg.get("reg_lambda", 1.0)), 0.5)
                else:
                    log_cfg = train_cfg.get("logistic", {})
                    max_iter = st.slider("max_iter", 100, 1000, int(log_cfg.get("max_iter", 500)), 50)

            with st.expander("Validation Settings", expanded=True):
                test_size = st.slider("Test split", 0.10, 0.40, float(train_cfg.get("test_size", 0.2)), 0.05)
                random_state = st.number_input("Random state", 0, 9999, int(train_cfg.get("random_state", 42)))

            with st.expander("DBSCAN Clustering", expanded=True):
                st.caption("Configure spatial clustering parameters.")
                db_cfg = train_cfg.get("dbscan", {})
                eps = st.slider("eps (neighborhood radius)", 0.1, 3.0, float(db_cfg.get("eps", 0.7)), 0.1)
                min_samples = st.slider("min_samples", 2, 20, int(db_cfg.get("min_samples", 6)), 1)

            if st.button("Train Models", type="primary", use_container_width=True):
                # Update config with user selections before training
                config["training"]["test_size"] = test_size
                config["training"]["random_state"] = random_state
                config["training"]["dbscan"]["eps"] = eps
                config["training"]["dbscan"]["min_samples"] = min_samples

                if model_choice.startswith("XGBoost"):
                    config["training"]["xgboost"]["n_estimators"] = n_est
                    config["training"]["xgboost"]["learning_rate"] = lr
                    config["training"]["xgboost"]["max_depth"] = depth
                    config["training"]["xgboost"]["subsample"] = subsample
                    config["training"]["xgboost"]["colsample_bytree"] = colsample
                    config["training"]["xgboost"]["reg_lambda"] = reg_lambda
                else:
                    config["training"]["logistic"]["max_iter"] = max_iter

                with st.spinner("Training models..."):
                    run_training_pipeline()
                st.cache_resource.clear()
                st.cache_data.clear()
                st.toast("Training complete!")
                st.rerun()

        with c_right:
            st.markdown('<div class="section-heading">Training Status</div>', unsafe_allow_html=True)
            if artifacts is not None:
                ibox(
                    "<strong>Models are trained and ready.</strong><br>"
                    "You can inspect results in the Evaluate tab or retrain with different settings.",
                    kind="ok",
                )
                st.markdown('<div class="section-heading">Current Configuration</div>', unsafe_allow_html=True)
                cfg_info = {
                    "Test Size": f"{config.get('training', {}).get('test_size', 0.2):.0%}",
                    "Random State": config.get("training", {}).get("random_state", 42),
                    "XGB n_estimators": config.get("training", {}).get("xgboost", {}).get("n_estimators"),
                    "XGB max_depth": config.get("training", {}).get("xgboost", {}).get("max_depth"),
                    "XGB learning_rate": config.get("training", {}).get("xgboost", {}).get("learning_rate"),
                    "DBSCAN eps": config.get("training", {}).get("dbscan", {}).get("eps"),
                    "DBSCAN min_samples": config.get("training", {}).get("dbscan", {}).get("min_samples"),
                }
                for k, v in cfg_info.items():
                    st.markdown(f"- **{k}:** `{v}`")
            else:
                ibox(
                    "<strong>Model belum dilatih.</strong><br>Klik tombol Train Models untuk melatih model.",
                    kind="warn",
                )

    with tab_eval:
        if metrics is None:
            st.info("Train a model first to see evaluation results here.")
            return

        # ── Macro metrics ──
        st.markdown('<div class="section-heading">Overall Performance</div>', unsafe_allow_html=True)
        mc = st.columns(4)
        for col, label, key in zip(
            mc,
            ["Macro F1", "Macro Precision", "Macro Recall", "Micro F1"],
            ["macro_f1", "macro_precision", "macro_recall", "micro_f1"],
        ):
            val = metrics.get(key, 0)
            col.markdown(
                f'<div class="metric-card" style="text-align:center">'
                f'<div class="label">{label}</div>'
                f'<div class="value" style="font-size:1.3rem">{val:.3f}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Interpretation
        macro_f1 = metrics.get("macro_f1", 0)
        perf_text = "Sangat Baik" if macro_f1 > 0.8 else ("Baik" if macro_f1 > 0.6 else "Perlu Ditingkatkan")
        ibox(
            f"<strong>Interpretasi Otomatis:</strong> Kinerja model berada di tingkat "
            f"<strong>{perf_text}</strong> (Macro F1: {macro_f1:.3f}). "
            f"{'Model cukup andal' if macro_f1 > 0.6 else 'Model kurang andal'} "
            f"untuk mengidentifikasi wilayah berisiko."
        )

        st.divider()

        # ── Confusion matrix & Per-class metrics ──
        col_cm, col_cls = st.columns(2)

        with col_cm:
            import plotly.express as px
            cm = metrics.get("confusion_matrix")
            if cm:
                risk_labels = config.get("risk_labels", {0: "Rendah", 1: "Sedang", 2: "Tinggi"})
                labels_list = [risk_labels.get(i, risk_labels.get(str(i), str(i))) for i in range(len(cm))]
                cm_df = pd.DataFrame(cm, columns=[f"Pred: {l}" for l in labels_list], index=[f"Actual: {l}" for l in labels_list])
                fig_cm = px.imshow(cm_df, text_auto=True, title="Confusion Matrix", color_continuous_scale="Blues")
                fig_cm.update_layout(margin=dict(t=40, b=10), coloraxis_showscale=False)
                st.plotly_chart(fig_cm, use_container_width=True)

        with col_cls:
            per_class = metrics.get("per_class")
            if per_class:
                st.markdown('<div class="section-heading">Per-Class Metrics</div>', unsafe_allow_html=True)
                risk_labels = config.get("risk_labels", {})
                cls_rows = []
                for cls_id, cls_metrics in per_class.items():
                    label = risk_labels.get(int(cls_id), risk_labels.get(cls_id, cls_id))
                    cls_rows.append({
                        "Risk Class": label,
                        "Precision": cls_metrics.get("precision", 0),
                        "Recall": cls_metrics.get("recall", 0),
                        "F1-Score": cls_metrics.get("f1", 0),
                    })
                cls_df = pd.DataFrame(cls_rows)
                st.dataframe(
                    cls_df.style.format({"Precision": "{:.3f}", "Recall": "{:.3f}", "F1-Score": "{:.3f}"}),
                    hide_index=True,
                    use_container_width=True,
                )


def page_spatial_map():
    page_header("Analisis Spasial", "Peta Risiko & Simulasi Skenario")

    col_map, col_sim = st.columns([70, 30], gap="large")

    with col_sim:
        sim_data = render_simulation(config, df, artifacts)

    with col_map:
        if artifacts is None:
            st.markdown('<div class="warn-box"><strong>Model belum dilatih.</strong><br>Silakan latih model terlebih dahulu.</div>', unsafe_allow_html=True)

        # Build a custom map that includes the simulation point
        render_heatmap(config, df_view)

        # Combined Simulation Results & Interpretation Box
        if sim_data is not None:
            result = sim_data["result"]
            delta_text = sim_data["delta_text"]
            pred_class = int(result.loc[0, "predicted_class"])
            pred_label = result.loc[0, "predicted_label"]
            prob = result.loc[0, "predicted_probability"]

            risk_colors = config.get("risk_colors", {0: "#10b981", 1: "#f59e0b", 2: "#ef4444"})
            color = risk_colors.get(pred_class, "#94a3b8")
            kind_class = {0: "ok-box", 1: "warn-box", 2: "risk-box"}.get(pred_class, "interp-box")

            html_content = f"""
            <div class="{kind_class}" style="margin-top: 1rem;">
                <div style="font-size: 0.95rem; color: var(--text-main);">
                    Tingkat risiko kesehatan wilayah yang disimulasikan diprediksi berada pada kategori
                    <strong style="color: {color};">{pred_label}</strong> dengan tingkat keyakinan (confidence) sebesar <strong>{prob:.2%}</strong>.
                </div>
            """

            if delta_text:
                html_content += f"""
                <hr style="border: 0; border-top: 1px solid var(--border); margin: 0.75rem 0;">
                <div style="font-size: 0.9rem; line-height: 1.6; color: var(--text-main);">
                    {delta_text}
                </div>
                """
            else:
                html_content += f"""
                <hr style="border: 0; border-top: 1px solid var(--border); margin: 0.75rem 0;">
                <div style="font-size: 0.9rem; line-height: 1.6; color: var(--text-muted); font-style: italic;">
                    Semua parameter berada pada nilai rata-rata (baseline). Ubah nilai parameter pada slider di sebelah kanan untuk menganalisis skenario alternatif (What-If).
                </div>
                """

            html_content += "</div>"
            st.markdown(html_content, unsafe_allow_html=True)


pg = st.navigation([
    st.Page(page_home,          title="Home",             default=True),
    st.Page(page_eda,           title="EDA"),
    st.Page(page_preprocessing, title="Preprocessing"),
    st.Page(page_train_eval,    title="Train & Evaluate"),
    st.Page(page_spatial_map,   title="Spatial Map"),
])

with st.sidebar:
    st.markdown('<div class="sidebar-info" style="font-weight:600; color:var(--primary); font-size:20px">BINUS University:</div>', unsafe_allow_html=True)
    for name in ["Anandhio Varistama", "Jason Tirta", "Muhammad Rizki Akbar"]:
        st.markdown(f'<div class="sidebar-info">{name}</div>', unsafe_allow_html=True)

pg.run()
