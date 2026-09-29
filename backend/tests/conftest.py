import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Point the app at a throwaway temp DB/dirs BEFORE importing app modules.
TEST_DIR = tempfile.mkdtemp(prefix="ai_ds_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DIR}/test_app.db"

from app.config import settings  # noqa: E402
settings.UPLOAD_DIR = os.path.join(TEST_DIR, "uploads")
settings.PROCESSED_DIR = os.path.join(TEST_DIR, "processed")
settings.MODELS_DIR = os.path.join(TEST_DIR, "models")
settings.REPORTS_DIR = os.path.join(TEST_DIR, "reports")
settings.LOG_DIR = os.path.join(TEST_DIR, "logs")
for d in (settings.UPLOAD_DIR, settings.PROCESSED_DIR, settings.MODELS_DIR, settings.REPORTS_DIR, settings.LOG_DIR):
    os.makedirs(d, exist_ok=True)

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.database import init_db  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _init_database():
    init_db()


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def sample_csv_path():
    import pandas as pd
    import numpy as np
    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame({
        "age": rng.integers(18, 70, n),
        "income": rng.normal(50000, 15000, n).round(2),
        "gender": rng.choice(["Male", "Female"], n),
        "city": rng.choice(["Lahore", "Karachi", "Islamabad"], n),
        "churned": rng.choice([0, 1], n, p=[0.7, 0.3]),
    })
    # introduce some missing values and duplicates on purpose
    df.loc[0:5, "income"] = np.nan
    df = pd.concat([df, df.iloc[:3]], ignore_index=True)

    path = os.path.join(TEST_DIR, "sample.csv")
    df.to_csv(path, index=False)
    return path
