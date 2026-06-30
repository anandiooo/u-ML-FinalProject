from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# resolve paths
def _resolve_path(value):
    if not value:
        return None
    return (PROJECT_ROOT / value).resolve()


# load config
def load_config(path=None):
    cfg_path = Path(path) if path else PROJECT_ROOT / "config.yaml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config not found: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    config["paths"] = {
        "root": PROJECT_ROOT,
        "data": _resolve_path(config["project"]["data_path"]),
        "geojson": _resolve_path(config["project"].get("geojson_path")),
        "model_dir": _resolve_path(config["project"]["model_dir"]),
    }
    return config
