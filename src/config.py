import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # ...\taxi
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

def _path_from_env(var_name: str, default_rel: str) -> Path:
    raw = os.getenv(var_name, default_rel)
    p = Path(raw)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p.resolve()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = False
    TESTING = False

    ROOT_DIR = PROJECT_ROOT
    BASE_DIR = Path(__file__).resolve().parent

    DATA_DIR = _path_from_env("DATA_DIR", "src/data")
    MODELS_DIR = _path_from_env("MODELS_DIR", "models")
    RESULTS_DIR = _path_from_env("RESULTS_DIR", "results")
    DATASET_PATH = _path_from_env("DATASET_PATH", "src/data/dataset.parquet")

    MLFLOW_TRACKING_URI = os.getenv(
        "MLFLOW_TRACKING_URI",
        (ROOT_DIR / "mlruns").resolve().as_uri()
    )
    MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "taxi-demand-models")

    @classmethod
    def ensure_dirs(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        cls.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (cls.ROOT_DIR / "mlruns").mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}