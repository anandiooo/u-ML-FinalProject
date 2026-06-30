import csv
from pathlib import Path

raw_file = Path("data/raw/kualitas_air_gabungan.csv")
processed_file = Path("data/processed/water_quality.csv")
processed_file.parent.mkdir(parents=True, exist_ok=True)
data_by_loc = {}
excluded_params = ["Status", "IP", "Bau", "Sampah", "Lapisan Minyak"]
with open(raw_file, "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        loc = row.get("lokasi_sampling")
        if not loc:
            continue
        if loc not in data_by_loc:
            data_by_loc[loc] = {
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "kondisi": None,
                "features": {},
            }
        if row.get("jenis_lokasi") != "Sumur" and row.get("kondisi"):
            data_by_loc[loc]["kondisi"] = row.get("kondisi")
        if row.get("parameter") == "Status" and row.get("hasil_pengukuran"):
            data_by_loc[loc]["kondisi"] = row.get("hasil_pengukuran")
        param = row.get("parameter")
        val_str = row.get("hasil_pengukuran", "")
        if param and param not in excluded_params:
            val_str = val_str.replace("< ", "").replace("<", "").strip()
            try:
                val = float(val_str)
                data_by_loc[loc]["features"][param] = val
            except ValueError:
                pass


# map risk
def map_risk(k):
    if not isinstance(k, str):
        return 0
    k = k.lower()
    if "baik" in k:
        return 0
    elif "ringan" in k:
        return 1
    elif "sedang" in k:
        return 2
    elif "berat" in k:
        return 3
    return 0


feature_counts = {}
for loc, data in data_by_loc.items():
    if data["latitude"] and data["longitude"]:
        for param in data["features"]:
            feature_counts[param] = feature_counts.get(param, 0) + 1
threshold = len(data_by_loc) * 0.2
valid_cols = [param for param, count in feature_counts.items() if count > threshold]
headers = [
    "lokasi_sampling",
    "latitude",
    "longitude",
    "kondisi",
    "risk_class",
] + valid_cols
written_rows = 0
with open(processed_file, "w", newline="", encoding="utf-8") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=headers)
    writer.writeheader()
    for loc, data in data_by_loc.items():
        if not data["latitude"] or not data["longitude"]:
            continue
        row_out = {
            "lokasi_sampling": loc,
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "kondisi": data["kondisi"],
            "risk_class": map_risk(data["kondisi"]),
        }
        for col in valid_cols:
            row_out[col] = data["features"].get(col, "")
        writer.writerow(row_out)
        written_rows += 1
print(f"Processed {written_rows} locations.")
print("Features saved:", valid_cols)
