import time


def test_full_workflow_end_to_end(client, sample_csv_path):
    # 1. Upload
    with open(sample_csv_path, "rb") as f:
        r = client.post("/api/datasets/upload", files={"file": ("sample.csv", f, "text/csv")})
    assert r.status_code == 201
    dataset_id = r.json()["id"]

    # 2. Start analysis (runs in a background task)
    r2 = client.post("/api/analysis", json={"dataset_id": dataset_id, "target_column": "churned"})
    assert r2.status_code == 202
    analysis_id = r2.json()["id"]

    # 3. Poll status until completed or failed (background task runs inline under TestClient)
    for _ in range(30):
        status_r = client.get(f"/api/analysis/{analysis_id}/status")
        assert status_r.status_code == 200
        st = status_r.json()["status"]
        if st in ("completed", "failed"):
            break
        time.sleep(0.5)

    assert st == "completed", status_r.json()

    # 4. Results contain real computed data
    results_r = client.get(f"/api/analysis/{analysis_id}/results")
    assert results_r.status_code == 200
    results = results_r.json()
    assert results["profiling"]["rows"] > 0
    assert results["ml_results"]["best_model_name"] is not None

    # 5. Chat works without an LLM key (rule-based grounded fallback)
    chat_r = client.post(f"/api/analysis/{analysis_id}/chat", json={"message": "Which model performed best?"})
    assert chat_r.status_code == 200
    assert chat_r.json()["grounded"] is True

    # 6. Report is downloadable
    report_r = client.get(f"/api/analysis/{analysis_id}/report")
    assert report_r.status_code == 200
    assert b"AI Data Science Report" in report_r.content


def test_analysis_for_nonexistent_dataset(client):
    r = client.post("/api/analysis", json={"dataset_id": 999999})
    assert r.status_code == 404


def test_status_for_nonexistent_analysis(client):
    r = client.get("/api/analysis/999999/status")
    assert r.status_code == 404
