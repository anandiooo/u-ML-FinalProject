import sys
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SaniSight AI",
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

with st.sidebar:
    st.markdown("### SaniSight AI")
    st.caption("Spatial-based health risk prediction")

    if st.button("Train / Refresh Models", type="primary", use_container_width=True):
        with st.spinner("Training models..."):
            run_training_pipeline()
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.write("Dataset:", config["project"]["data_path"])
    if artifacts is None:
        st.warning("Models not found. Train to enable predictions.")


def page_dashboard():
    page_header("SaniSight AI", "Spatial-based health risk prediction system")
    render_dashboard(config, df_view, metrics)


def page_spatial_analysis():
    page_header("Spatial Analysis", "Heatmap & Scenario Simulator")
    
    col_map, col_sim = st.columns([3, 1], gap="large")
    
    with col_map:
        if artifacts is None:
            ibox("<strong>No models found.</strong><br>Train models to render predictions on the map.", kind="warn")
        render_heatmap(config, df_view)
        
    with col_sim:
        render_simulation(config, df, artifacts)


def page_data():
    page_header("Exploratory Data Analysis", "Raw and enriched dataset view")
    render_data(config, df_view)


pg = st.navigation([
    st.Page(page_dashboard, title="Dashboard Overview", default=True),
    st.Page(page_spatial_analysis, title="Spatial Analysis"),
    st.Page(page_data, title="EDA"),
])

pg.run()
