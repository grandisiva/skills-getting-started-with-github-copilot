import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities state before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })
    yield
    activities.clear()


def test_get_activities(client):
    """Test GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert len(data) == 3


def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_error(client):
    """Test signup error when student already registered"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity_error(client):
    """Test signup error for nonexistent activity"""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_removal_success(client):
    """Test successful removal of participant from activity"""
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_removal_not_found_error(client):
    """Test removal error when participant not found in activity"""
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "nonexistent@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_removal_nonexistent_activity_error(client):
    """Test removal error for nonexistent activity"""
    response = client.delete(
        "/activities/Nonexistent Activity/participants",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
