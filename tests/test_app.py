import sys
from pathlib import Path
import importlib

# Ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app as app_module
from fastapi.testclient import TestClient


def setup_function():
    # reload module to reset in-memory state between tests
    importlib.reload(app_module)


def test_get_activities():
    client = TestClient(app_module.app)
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_duplicate():
    client = TestClient(app_module.app)
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # sign up should succeed
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # duplicate signup should return 400
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400


def test_unregister_and_errors():
    client = TestClient(app_module.app)
    activity = "Programming Class"
    email = "temp@student.edu"

    # unregister when not registered should return 400
    r = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert r.status_code == 400

    # sign up then unregister
    r1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r1.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    r2 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert r2.status_code == 200
    assert email not in app_module.activities[activity]["participants"]


def test_missing_activity_returns_404():
    client = TestClient(app_module.app)
    r = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert r.status_code == 404
