# SaniSight: Spatial-Based Health Risk Prediction System

SaniSight is a data-driven Spatial Decision Support System built for our Machine Learning Final Project at BINUS University. It proactively predicts health risk levels in regional areas based on environmental data (sanitation quality, clean water access, waste volume, etc.) using classical machine learning techniques.

### Team Members
- Anandhio Varistama
- Jason Tirta
- Muhammad Rizki Akbar

---

## Features
- **End-to-End Pipeline:** Automated data preprocessing, missing value imputation, outlier handling, and scaling.
- **Multi-Model Support:** Includes XGBoost (Primary Classifier) and Logistic Regression (Baseline).
- **Spatial Clustering:** Utilizes DBSCAN to cluster regions geographically based on health risk.
- **Interactive UI:** Built with Streamlit, featuring Exploratory Data Analysis (EDA), model training interfaces, evaluation metrics, and a "What-If" scenario simulation map.

---

## Setup & Installation

**1. Clone the repository:**
```bash
git clone https://github.com/anandiooo/u-ML-FinalProject.git
cd u-ML-FinalProject
```

**2. Create a virtual environment (Optional but recommended):**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

**3. Install the dependencies:**
```bash
pip install -r requirements.txt
```

---

## Running the Application

To launch the interactive dashboard, simply run:
```bash
streamlit run streamlit_app.py
```

The application will automatically open in your default web browser (usually at `http://localhost:8501`).

---

## Project Structure
- `streamlit_app.py`: The main entry point for the Streamlit dashboard.
- `src/`: Core modular backend logic (data preprocessing, modeling, UI components).
- `data/`: Contains raw datasets (`data/raw/`) and processed datasets (`data/processed/`).
- `models/`: Stores the trained `.joblib` model artifacts and evaluation metrics.
- `config.yaml`: Configuration file for adjusting features, model hyperparameters, and risk labels.
- `deliverables/`: Contains the final project report and other submission materials.

---

## Technologies Used
- **Python 3**
- **Machine Learning:** `scikit-learn`, `xgboost`
- **Data Manipulation:** `pandas`, `numpy`
- **Web Framework:** `streamlit`
- **Visualization:** `folium` (Maps), `plotly` (Charts)
