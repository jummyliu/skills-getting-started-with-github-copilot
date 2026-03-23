import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


client = TestClient(app)


def test_get_activities():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload


def test_signup_success_and_duplicate():
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    uri = f"/activities/{quote(activity)}/signup?email={quote(email)}"

    # first signup succeeds
    response1 = client.post(uri)
    assert response1.status_code == 200
    assert "Signed up" in response1.json()["message"]
    assert email in activities[activity]["participants"]

    # second signup fails with duplicate
    response2 = client.post(uri)
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_remove_participant():
    activity = "Chess Club"
    email = "removeme@mergington.edu"
    activities[activity]["participants"].append(email)

    uri = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    response = client.delete(uri)

    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found():
    activity = "Chess Club"
    email = "missing@mergington.edu"
    uri = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    response = client.delete(uri)

    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]
