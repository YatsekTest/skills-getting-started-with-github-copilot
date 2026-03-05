"""
Tests for the High School Management System API

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
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
        },
        "Basketball Team": {
            "description": "Join our competitive basketball team and participate in matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Develop tennis skills and compete in tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and improve acting skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and argumentation skills",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["liam@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        }
    })
    yield


# ============================================================================
# GET /activities Tests
# ============================================================================

def test_get_activities():
    """Test retrieving all activities"""
    # Arrange
    activity_name = "Chess Club"
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert activity_name in data
    assert "description" in data[activity_name]
    assert "schedule" in data[activity_name]
    assert "max_participants" in data[activity_name]
    assert "participants" in data[activity_name]
    assert isinstance(data[activity_name]["participants"], list)


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    new_student_email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={new_student_email}"
    )
    
    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    assert new_student_email in response.json()["message"]
    
    # Verify participant was added
    get_response = client.get("/activities")
    assert new_student_email in get_response.json()[activity_name]["participants"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    # Arrange
    non_existent_activity = "NonExistent Club"
    student_email = "test@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{non_existent_activity}/signup?email={student_email}"
    )
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_duplicate():
    """Test signup fails when student is already signed up"""
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "duplicate@mergington.edu"
    
    # Act - First signup should succeed
    first_response = client.post(
        f"/activities/{activity_name}/signup?email={duplicate_email}"
    )
    assert first_response.status_code == 200
    
    # Act - Second signup with same email should fail
    second_response = client.post(
        f"/activities/{activity_name}/signup?email={duplicate_email}"
    )
    
    # Assert
    assert second_response.status_code == 400
    assert "already signed up" in second_response.json()["detail"]


# ============================================================================
# DELETE /activities/{activity_name}/participants/{email} Tests
# ============================================================================

def test_unregister_success():
    """Test successful unregistration from an activity"""
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"
    
    # Verify participant exists before deletion
    get_response = client.get("/activities")
    assert participant_email in get_response.json()[activity_name]["participants"]
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{participant_email}"
    )
    
    # Assert
    assert response.status_code == 200
    assert participant_email in response.json()["message"]
    
    # Verify participant was removed
    get_response_after = client.get("/activities")
    assert participant_email not in get_response_after.json()[activity_name]["participants"]


def test_unregister_activity_not_found():
    """Test unregistration from non-existent activity"""
    # Arrange
    non_existent_activity = "NonExistent Club"
    participant_email = "test@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{non_existent_activity}/participants/{participant_email}"
    )
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_participant_not_found():
    """Test unregistration of participant not in activity"""
    # Arrange
    activity_name = "Chess Club"
    non_existent_participant = "nonexistent@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{non_existent_participant}"
    )
    
    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


# ============================================================================
# Root endpoint test
# ============================================================================

def test_root_redirect():
    """Test root endpoint redirects to static index"""
    # Arrange
    # (No special setup needed)
    
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    assert "Mergington High School" in response.text
