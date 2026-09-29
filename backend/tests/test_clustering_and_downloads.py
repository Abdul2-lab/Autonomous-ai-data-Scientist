import io
import time

import numpy as np
import pandas as pd

from app.agents.clustering_agent import ClusteringAgent
from app.utils.helpers import identifier_like_columns


def _blobs(n_per=60):
    rng = np.random.default_rng(3)
    a = rng.normal([0, 0], 0.4, (n_per, 2))
    b = rng.normal([6, 6], 0.4, (n_per, 2))
    c = rng.normal([0, 7], 0.4, (n_per, 2))
    X = np.vstack([a, b, c])
    return pd.DataFrame({"f1": X[:, 0], "f2": X[:, 1]})


def test_clustering_agent_finds_three_obvious_groups():
    df = _blobs()
    result = ClusteringAgent().run(df, ["f1", "f2"], [], analysis_id=501)
    assert result["available"] is True
    assert result["best_k"] == 3
    assert result["silhouette"] > 0.4
    assert sum(c["size"] for c in result["clusters"]) == len(df)
    assert len(result["pca_points"]) > 0
    assert result["distinguishing_features"]


def test_clustering_agent_handles_categorical_features():
    df = _blobs()
    df["grp"] = np.random.default_rng(4).choice(["x", "y"], len(df))
    result = ClusteringAgent().run(df, ["f1", "f2"], ["grp"], analysis_id=503)
    assert result["available"] is True
    assert "grp" in result["features_used"]
    assert all("top_value" in v for cl in result["clusters"] for v in cl["categorical_top"].values())


def test_clustering_agent_refuses_tiny_data():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    result = ClusteringAgent().run(df, ["a", "b"], [], analysis_id=502)
    assert result["available"] is False
    assert "reason" in result


def test_identifier_like_columns_detected():
    df = pd.DataFrame({
        "customer_id": [f"C{i}" for i in range(100)],
        "age": np.random.default_rng(1).integers(20, 60, 100),
        "city": ["a", "b"] * 50,
    })
    assert identifier_like_columns(df) == ["customer_id"]


def _make_csv(with_target=True):
    rng = np.random.default_rng(9)
    n = 240
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    df = pd.DataFrame({
        "customer_id": [f"CUST{i}" for i in range(n)],
        "x1": x1, "x2": x2,
        "city": rng.choice(["A", "B", "C"], n),
        "label": (x1 + x2 + rng.normal(0, 0.5, n) > 0).astype(int),
    })
    df.loc[0:4, "x1"] = np.nan
    df = pd.concat([df, df.iloc[:4]], ignore_index=True)  # 4 duplicates
    return df.to_csv(index=False).encode()


def _run(client, csv_bytes, target):
    up = client.post("/api/datasets/upload", files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")})
    assert up.status_code == 201
    r = client.post("/api/analysis", json={"dataset_id": up.json()["id"], "target_column": target})
    assert r.status_code == 202
    aid = r.json()["id"]
    for _ in range(60):
        st = client.get(f"/api/analysis/{aid}/status").json()
        if st["status"] in ("completed", "failed"):
            break
        time.sleep(0.5)
    assert st["status"] == "completed", st
    return aid


def test_no_target_runs_real_clustering_end_to_end(client):
    aid = _run(client, _make_csv(), None)
    res = client.get(f"/api/analysis/{aid}/results").json()
    assert res["problem_type"] == "clustering"
    clustering = res["ml_results"]["clustering"]
    assert clustering["available"] is True
    assert "customer_id" not in clustering["features_used"]  # ID column excluded
    assert res["ml_results"]["best_model_name"].startswith("KMeans")
    assert any("clustering" in f.lower() for f in res["insights"]["key_findings"])
    # no server paths leaked
    assert "model_path" not in clustering
    assert "processed_file_path" not in res["cleaning"]


def test_supervised_run_has_roc_curve_and_excludes_id(client):
    aid = _run(client, _make_csv(), "label")
    res = client.get(f"/api/analysis/{aid}/results").json()
    ml = res["ml_results"]
    assert ml["problem_type"] == "classification"
    assert "customer_id" in ml["excluded_columns"]
    assert "customer_id" not in ml["feature_columns"]
    best = next(e for e in ml["experiments"] if e["model_name"] == ml["best_model_name"])
    assert best["metrics"]["roc_curve"]["fpr"][0] == 0.0
    assert "best_model_path" not in ml


def test_cleaned_dataset_download_is_clean_and_separate(client):
    aid = _run(client, _make_csv(), "label")
    r = client.get(f"/api/analysis/{aid}/cleaned-dataset")
    assert r.status_code == 200
    assert "attachment" in r.headers["content-disposition"]
    assert "cleaned_data.csv" in r.headers["content-disposition"]
    cleaned = pd.read_csv(io.BytesIO(r.content))
    assert len(cleaned) == 240            # 4 duplicates removed from 244
    assert cleaned["x1"].isnull().sum() == 0  # missing values filled


def test_export_json_and_missing_analysis(client):
    aid = _run(client, _make_csv(), "label")
    r = client.get(f"/api/analysis/{aid}/export")
    assert r.status_code == 200
    body = r.json()
    assert body["analysis_id"] == aid and body["ml_results"]["best_model_name"]
    assert "processed_file_path" not in body["cleaning"]
    assert client.get("/api/analysis/999999/cleaned-dataset").status_code == 404
    assert client.get("/api/analysis/999999/export").status_code == 404
