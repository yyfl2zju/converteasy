from io import BytesIO


def test_detect_targets_document(client):
    file_content = BytesIO(b"dummy content")
    files = {"file": ("sample.docx", file_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {"category": "document"}
    resp = client.post("/detect-targets", files=files, data=data)
    assert resp.status_code == 200
    body = resp.json()
    assert body["filename"] == "sample.docx"
    assert body["category"] == "document"
    assert isinstance(body["supportedTargets"], list)
    assert body["canConvert"] in (True, False)


def test_detect_targets_invalid_category(client):
    file_content = BytesIO(b"dummy content")
    files = {"file": ("sample.docx", file_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {"category": "video"}
    resp = client.post("/detect-targets", files=files, data=data)
    assert resp.status_code == 400
