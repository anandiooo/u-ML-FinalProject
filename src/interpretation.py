import pandas as pd


# explain eda
def generate_eda_interpretation(feature_name, df, target_col, config):
    if df is None or feature_name not in df.columns or target_col not in df.columns:
        return ""
    risk_labels = config.get(
        "risk_labels", {0: "Risiko Rendah", 1: "Risiko Sedang", 2: "Risiko Tinggi"}
    )
    is_numeric = pd.api.types.is_numeric_dtype(df[feature_name])
    if is_numeric:
        means = df.groupby(target_col)[feature_name].mean()
        mean_low = means.get(0, 0)
        mean_high = means.get(2, 0)
        if pd.isna(mean_low) or pd.isna(mean_high):
            return "Insufficient data for automatic interpretation."
        diff_pct = abs(mean_high - mean_low) / (mean_low + 1e-05) * 100
        direction = "higher" if mean_high > mean_low else "lower"
        strength = (
            "Strong" if diff_pct > 20 else "Moderate" if diff_pct > 10 else "Weak"
        )
        feature_display = feature_name.replace("_", " ").title()
        interp = f"<strong>Auto Interpretation:</strong> High-risk areas have an average *{feature_display}* of <strong>{mean_high:.1f}</strong>, which is <strong>{direction}</strong> compared to low-risk areas ({mean_low:.1f}). This {diff_pct:.1f}% difference indicates that this indicator has a <strong>{strength}</strong> predictive signal for health risk."
        return interp
    return "Automatic analysis for categorical features is not yet available."


# explain corr
def generate_correlation_interpretation(df, target_col, features, config):
    if df is None or target_col not in df.columns:
        return ""
    corr = df[features + [target_col]].corr()[target_col].drop(target_col)
    corr_abs = corr.abs().sort_values(ascending=False)
    if len(corr_abs) == 0:
        return ""
    top_feature = corr_abs.index[0]
    top_val = corr.loc[top_feature]
    direction = "positively correlated" if top_val > 0 else "negatively correlated"
    return f"<strong>Auto Interpretation:</strong> *{top_feature.replace('_', ' ').title()}* is the strongest predictor with a correlation of {top_val:.2f}. This means this indicator is <strong>{direction}</strong> with health risk level. Variables with absolute correlation > 0.3 are critical in regional planning."


# explain sim
def generate_simulation_delta(baseline_inputs, current_inputs, current_result, config):
    FEATURE_LABELS = {
        "kepadatan_penduduk": "Kepadatan Penduduk",
        "pct_tanpa_sanitasi": "% Tanpa Sanitasi",
        "pct_tanpa_air_bersih": "% Tanpa Air Bersih",
        "volume_sampah_harian": "Volume Sampah Harian",
        "curah_hujan_mm": "Curah Hujan",
        "indeks_kualitas_air": "Indeks Kualitas Air",
        "jumlah_faskes_per_1000": "Faskes per 1.000",
    }
    changes = []
    for k, v in current_inputs.items():
        base_v = baseline_inputs.get(k, v)
        if abs(v - base_v) > 0.01:
            direction = "increased" if v > base_v else "decreased"
            display_name = FEATURE_LABELS.get(k, k.replace("_", " ").title())
            pct_change = abs(v - base_v) / (abs(base_v) + 1e-05) * 100
            changes.append(
                f"<strong>{display_name}</strong> {direction} from {base_v:.1f} → {v:.1f} ({pct_change:.0f}%)"
            )
    if not changes:
        return ""
    changes_str = "<br>• ".join(changes)
    risk_label = current_result.loc[0, "predicted_label"]
    return f"<strong>What-If Scenario:</strong><br>Parameter changes you made:<br>• {changes_str}<br><br>Based on these environmental condition changes, the model predicts the region will fall into the <strong>{risk_label}</strong> category. This information helps local governments anticipate impacts before a crisis occurs."
