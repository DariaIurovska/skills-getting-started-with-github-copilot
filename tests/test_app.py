import uuid

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "participants" in activities["Chess Club"]
    assert isinstance(activities["Chess Club"]["participants"], list)


def test_signup_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = f"student-{uuid.uuid4().hex[:8]}@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Signed up {email} for {activity_name}"

    get_response = client.get("/activities")
    assert get_response.status_code == 200
    activities = get_response.json()
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_error():
    # Arrange
    activity_name = "Chess Club"
    email = f"student-{uuid.uuid4().hex[:8]}@mergington.edu"
    first_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert first_response.status_code == 200

    # Act
    duplicate_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert duplicate_response.status_code == 400
    payload = duplicate_response.json()
    assert payload["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = f"student-{uuid.uuid4().hex[:8]}@mergington.edu"
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert signup_response.status_code == 200

    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/participants?email={email}"
    )

    # Assert
    assert delete_response.status_code == 200
    payload = delete_response.json()
    assert payload["message"] == f"Removed {email} from {activity_name}"

    get_response = client.get("/activities")
    assert get_response.status_code == 200
    activities = get_response.json()
    assert email not in activities[activity_name]["participants"]
