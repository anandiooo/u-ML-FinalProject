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
            f"<strong>Interpretasi Otomatis:</strong> Wilayah dengan Risiko Tinggi memiliki rata-rata *{feature_display}* "
            f"sebesar <strong>{mean_high:.1f}</strong>, yang mana <strong>{direction}</strong> dibandingkan dengan wilayah Risiko Rendah "
            f"({mean_low:.1f}). Perbedaan sebesar {diff_pct:.1f}% ini menunjukkan bahwa indikator ini memiliki "
            f"sinyal prediksi yang <strong>{strength}</strong> terhadap risiko kesehatan."
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
        f"<strong>Interpretasi Otomatis:</strong> *{top_feature.replace('_', ' ').title()}* adalah prediktor terkuat "
        f"dengan korelasi {top_val:.2f}. Artinya, indikator ini <strong>{direction}</strong> dengan tingkat risiko kesehatan. "
        f"Variabel dengan nilai korelasi absolut > 0.3 sangat penting dalam perencanaan wilayah."
    )


def generate_simulation_delta(baseline_inputs, current_inputs, current_result, config):
    """Produces a what-if comparison narrative between baseline and current simulation."""

    FEATURE_LABELS = {
        "kepadatan_penduduk": "Kepadatan Penduduk",
        "pct_tanpa_sanitasi": "% Tanpa Sanitasi",
        "pct_tanpa_air_bersih": "% Tanpa Air Bersih",
        "volume_sampah_harian": "Volume Sampah Harian",
        "curah_hujan_mm": "Curah Hujan",
        "indeks_kualitas_air": "Indeks Kualitas Air",
        "jumlah_faskes_per_1000": "Faskes per 1.000",
    }

    # Identify what changed (ignore tiny differences from float rounding)
    changes = []
    for k, v in current_inputs.items():
        base_v = baseline_inputs.get(k, v)
        if abs(v - base_v) > 0.01:
            direction = "meningkat" if v > base_v else "menurun"
            display_name = FEATURE_LABELS.get(k, k.replace("_", " ").title())
            pct_change = abs(v - base_v) / (abs(base_v) + 1e-5) * 100
            changes.append(
                f"<strong>{display_name}</strong> {direction} dari {base_v:.1f} → {v:.1f} "
                f"({pct_change:.0f}%)"
            )

    if not changes:
        return ""

    changes_str = "<br>• ".join(changes)
    risk_label = current_result.loc[0, "predicted_label"]

    return (
        f"<strong>Skenario Simulasi (What-If):</strong><br>"
        f"Perubahan parameter yang Anda lakukan:<br>• {changes_str}<br><br>"
        f"Berdasarkan perubahan kondisi lingkungan ini, model memprediksi wilayah ini akan masuk ke kategori "
        f"<strong>{risk_label}</strong>. Informasi ini membantu pemerintah daerah mengantisipasi dampak "
        f"sebelum krisis terjadi."
    )
