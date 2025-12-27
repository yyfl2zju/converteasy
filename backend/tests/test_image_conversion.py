import time
import pytest
from pathlib import Path

SAMPLES_DIR = Path(__file__).parent / "samples"


def test_detect_targets_image(client):
    """Test detecting targets for an image file"""
    sample_jpg = SAMPLES_DIR / "sample.jpg"
    if not sample_jpg.exists():
        pytest.skip("sample.jpg not found")

    with open(sample_jpg, "rb") as f:
        response = client.post(
            "/detect-targets",
            files={"file": ("sample.jpg", f, "image/jpeg")},
            data={"category": "image"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "image"
    assert data["sourceExtension"] == ".jpg"
    assert "png" in data["supportedTargets"]
    assert "pdf" in data["supportedTargets"]


def test_image_conversion_jpg_to_png(client):
    """Test converting JPG to PNG"""
    sample_jpg = SAMPLES_DIR / "sample.jpg"
    if not sample_jpg.exists():
        pytest.skip("sample.jpg not found")

    # 1. Upload and start conversion
    with open(sample_jpg, "rb") as f:
        response = client.post(
            "/convert/upload",
            files={"file": ("sample.jpg", f, "image/jpeg")},
            data={"category": "image", "target": "png"},
        )

    assert response.status_code == 200
    task_id = response.json()["taskId"]
    assert task_id

    # 2. Poll for completion
    max_retries = 30
    for _ in range(max_retries):
        response = client.get(f"/convert/task/{task_id}")
        assert response.status_code == 200
        data = response.json()
        if data["state"] in ["finished", "error"]:
            break
        time.sleep(0.5)

    assert data["state"] == "finished"
    assert data["url"]
    assert data["url"].endswith(".png")


def test_image_conversion_png_to_pdf(client):
    """Test converting PNG to PDF"""
    sample_png = SAMPLES_DIR / "sample.png"
    if not sample_png.exists():
        pytest.skip("sample.png not found")

    # 1. Upload and start conversion
    with open(sample_png, "rb") as f:
        response = client.post(
            "/convert/upload",
            files={"file": ("sample.png", f, "image/png")},
            data={"category": "image", "target": "pdf"},
        )

    assert response.status_code == 200
    task_id = response.json()["taskId"]
    assert task_id

    # 2. Poll for completion
    max_retries = 30
    for _ in range(max_retries):
        response = client.get(f"/convert/task/{task_id}")
        assert response.status_code == 200
        data = response.json()
        if data["state"] in ["finished", "error"]:
            break
        time.sleep(0.5)

    assert data["state"] == "finished"
    assert data["url"]
    assert data["url"].endswith(".pdf")
