import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    def test_get_root_redirects_to_static_index(self):
        # Arrange - no special setup needed
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    def test_get_activities_returns_all_activities(self):
        # Arrange - no special setup needed
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) >= 9  # At least the pre-loaded activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    def test_post_signup_successful_for_new_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_post_signup_fails_for_nonexistent_activity(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_post_signup_fails_for_duplicate_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "Student already signed up" in result["detail"]


class TestRemoveParticipantEndpoint:
    def test_delete_participant_successful_for_existing_participant(self):
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already in participants
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_delete_participant_fails_for_nonexistent_activity(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_delete_participant_fails_for_nonexistent_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Participant not found" in result["detail"]


# Known limitations (documented for future improvements):
# - No email format validation (accepts any string as email)
# - No capacity enforcement (can sign up beyond max_participants)
# - No input sanitization for activity names or emails