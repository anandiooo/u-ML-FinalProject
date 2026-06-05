import importlib.util
import pytest

from src.pipelines import run_training_pipeline


if importlib.util.find_spec("xgboost") is None:
    pytest.skip("xgboost not installed", allow_module_level=True)


def test_training_pipeline_runs():
    metrics = run_training_pipeline()
    assert "macro_f1" in metrics
