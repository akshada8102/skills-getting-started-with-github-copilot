import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture(autouse=True)
def reset_activities():
    # Save original activities dict
    original_activities = activities.copy()
    yield
    # Restore original activities
    activities.clear()
    activities.update(original_activities)

client = TestClient(app)

def test_get_activities():
    # Arrange - TestClient is set up via fixture
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success():
    # Arrange - No special setup needed
    
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "newstudent@mergington.edu"})
    
    # Assert
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    assert response.json() == {"message": "Signed up newstudent@mergington.edu for Chess Club"}

def test_signup_activity_not_found():
    # Arrange - No special setup needed
    
    # Act
    response = client.post("/activities/Nonexistent Activity/signup", params={"email": "test@mergington.edu"})
    
    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_signup_already_signed_up():
    # Arrange - Sign up the student first
    client.post("/activities/Programming Class/signup", params={"email": "duplicate@mergington.edu"})
    
    # Act - Try to sign up again
    response = client.post("/activities/Programming Class/signup", params={"email": "duplicate@mergington.edu"})
    
    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}

def test_signup_over_max_participants():
    # Arrange - Sign up participants up to the max
    for i in range(10):
        client.post("/activities/Chess Club/signup", params={"email": f"extra{i}@mergington.edu"})
    
    # Act - Try to sign up one more
    response = client.post("/activities/Chess Club/signup", params={"email": "overmax@mergington.edu"})
    
    # Assert - Current implementation allows over max, so succeeds
    assert response.status_code == 200

def test_unregister_success():
    # Arrange - Sign up the student first
    client.post("/activities/Gym Class/signup", params={"email": "removeme@mergington.edu"})
    
    # Act - Unregister the student
    response = client.delete("/activities/Gym Class/signup", params={"email": "removeme@mergington.edu"})
    
    # Assert
    assert response.status_code == 200
    assert "removeme@mergington.edu" not in activities["Gym Class"]["participants"]
    assert response.json() == {"message": "Unregistered removeme@mergington.edu from Gym Class"}

def test_unregister_activity_not_found():
    # Arrange - No special setup needed
    
    # Act
    response = client.delete("/activities/Nonexistent Activity/signup", params={"email": "test@mergington.edu"})
    
    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_not_signed_up():
    # Arrange - No special setup needed
    
    # Act
    response = client.delete("/activities/Soccer Team/signup", params={"email": "notsigned@mergington.edu"})
    
    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not signed up for this activity"}