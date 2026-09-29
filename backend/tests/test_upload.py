def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_upload_valid_csv(client, sample_csv_path):
    with open(sample_csv_path, "rb") as f:
        r = client.post("/api/datasets/upload", files={"file": ("sample.csv", f, "text/csv")})
    assert r.status_code == 201
    body = r.json()
    assert body["rows"] == 203  # 200 + 3 duplicated rows
    assert body["columns"] == 5
    assert body["status"] == "uploaded"


def test_upload_rejects_bad_extension(client, tmp_path):
    bad_file = tmp_path / "malware.exe"
    bad_file.write_bytes(b"not a dataset")
    with open(bad_file, "rb") as f:
        r = client.post("/api/datasets/upload", files={"file": ("malware.exe", f, "application/octet-stream")})
    assert r.status_code == 400


def test_upload_rejects_empty_file(client, tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_bytes(b"")
    with open(empty_file, "rb") as f:
        r = client.post("/api/datasets/upload", files={"file": ("empty.csv", f, "text/csv")})
    assert r.status_code == 400


def test_get_dataset_preview(client, sample_csv_path):
    with open(sample_csv_path, "rb") as f:
        r = client.post("/api/datasets/upload", files={"file": ("sample.csv", f, "text/csv")})
    dataset_id = r.json()["id"]

    r2 = client.get(f"/api/datasets/{dataset_id}")
    assert r2.status_code == 200
    body = r2.json()
    assert "age" in body["columns"]
    assert len(body["preview_rows"]) <= 20


def test_get_nonexistent_dataset(client):
    r = client.get("/api/datasets/999999")
    assert r.status_code == 404
