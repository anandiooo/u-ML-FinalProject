from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class Preprocessor:
    def __init__(self, features):
        self.features = features
        self.scaler = StandardScaler()

    def fit_transform(self, df):
        X = df[self.features].copy()
        X = X.apply(pd.to_numeric, errors="coerce")
        X = X.fillna(X.median(numeric_only=True))
        self.scaler.fit(X)
        return self.scaler.transform(X)

    def transform(self, df):
        X = df[self.features].copy()
        X = X.apply(pd.to_numeric, errors="coerce")
        X = X.fillna(X.median(numeric_only=True))
        return self.scaler.transform(X)


def load_dataset(config, create_if_missing=True):
    data_path = Path(config["paths"]["data"])
    if data_path.exists():
        df = pd.read_csv(data_path)
        if "latitude" in df.columns:
            df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        if "longitude" in df.columns:
            df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
        return df

    raise FileNotFoundError(
        f"Processed dataset not found at {data_path}. "
        "Please run 'python src/prepare_data.py' first."
    )
