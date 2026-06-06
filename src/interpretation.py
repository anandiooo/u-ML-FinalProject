import numpy as np
import pandas as pd


def generate_eda_interpretation(feature_name, df, target_col, config):
    """Auto-generates chart interpretation text for EDA."""

    if df is None or feature_name not in df.columns or target_col not in df.columns:
        return ""
        
    risk_labels = config.get("risk_labels", {0: "Rendah", 1: "Sedang", 2: "Tinggi"})

    is_numeric = pd.api.types.is_numeric_dtype(df[feature_name])

    if is_numeric:
        # Calculate means for each risk group
        means = df.groupby(target_col)[feature_name].mean()

        # Get mean for low risk (0) and high risk (2)
        mean_low = means.get(0, 0)
        mean_high = means.get(2, 0)

        if pd.isna(mean_low) or pd.isna(mean_high):
            return "Data tidak cukup untuk interpretasi otomatis."

        diff_pct = abs(mean_high - mean_low) / (mean_low + 1e-5) * 100
        direction = "lebih tinggi" if mean_high > mean_low else "lebih rendah"

        strength = "Kuat" if diff_pct > 20 else ("Sedang" if diff_pct > 10 else "Lemah")

        feature_display = feature_name.replace("_", " ").title()

        interp = (
            f"**Interpretasi Otomatis:** Wilayah dengan Risiko Tinggi memiliki rata-rata *{feature_display}* "
            f"sebesar **{mean_high:.1f}**, yang mana **{direction}** dibandingkan dengan wilayah Risiko Rendah "
            f"({mean_low:.1f}). Perbedaan sebesar {diff_pct:.1f}% ini menunjukkan bahwa indikator ini memiliki "
            f"sinyal prediksi yang **{strength}** terhadap risiko kesehatan."
        )
        return interp

    return "Analisis otomatis untuk fitur kategorikal belum tersedia."


def generate_correlation_interpretation(df, target_col, features, config):
    """Finds the strongest correlate to target and explains it."""

    if df is None or target_col not in df.columns:
        return ""

    corr = df[features + [target_col]].corr()[target_col].drop(target_col)
    corr_abs = corr.abs().sort_values(ascending=False)

    if len(corr_abs) == 0:
        return ""

    top_feature = corr_abs.index[0]
    top_val = corr.loc[top_feature]

    direction = "berbanding lurus" if top_val > 0 else "berbanding terbalik"

    return (
        f"**Interpretasi Otomatis:** *{top_feature.replace('_', ' ').title()}* adalah prediktor terkuat "
        f"dengan korelasi {top_val:.2f}. Artinya, indikator ini **{direction}** dengan tingkat risiko kesehatan. "
        f"Variabel dengan nilai korelasi absolut > 0.3 sangat penting dalam perencanaan wilayah."
    )


def generate_simulation_delta(baseline_inputs, current_inputs, current_result, config):
    """Produces a what-if comparison narrative between baseline and current simulation."""

    # Identify what changed
    changes = []
    for k, v in current_inputs.items():
        base_v = baseline_inputs.get(k, v)
        if base_v != v:
            direction = "meningkat" if v > base_v else "menurun"
            changes.append(f"{k.replace('_', ' ')} {direction} dari {base_v:.1f} menjadi {v:.1f}")

    if not changes:
        return ""

    changes_str = ", ".join(changes)
    risk_label = current_result.loc[0, "predicted_label"]

    return (
        f"**Skenario Simulasi (What-If):** Anda mengubah simulasi di mana {changes_str}. "
        f"Berdasarkan perubahan kondisi lingkungan ini, model memprediksi wilayah ini akan masuk ke kategori "
        f"**{risk_label}**. Ini membantu pemerintah daerah mengantisipasi dampak sebelum krisis terjadi."
    )
