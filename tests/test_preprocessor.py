import pandas as pd

from src.preprocessor import Preprocessor


def test_preprocessor_scales_features():
    df = pd.DataFrame(
        {
            "kepadatan_penduduk": [1000, 2000, 3000],
            "pct_akses_air_bersih": [10, 20, 30],
        }
    )
    prep = Preprocessor(["kepadatan_penduduk", "pct_akses_air_bersih"])
    X = prep.fit_transform(df)
    assert X.shape == (3, 2)
