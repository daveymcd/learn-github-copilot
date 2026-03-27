"""
Tests for the Mergington High School API endpoints.

This module contains comprehensive tests for all API endpoints using the
AAA (Arrange-Act-Assert) testing pattern. Tests cover both happy-path
scenarios and error cases.
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Test cases for GET /activities endpoint."""

    def test_get_all_activities_returns_correct_structure(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        # Arrange - No special setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()

        # Check that we have activities
        assert isinstance(activities, dict)
        assert len(activities) > 0

        # Check structure of first activity
        first_activity = next(iter(activities.values()))
        required_keys = ["description", "schedule", "max_participants", "participants"]
        for key in required_keys:
            assert key in first_activity

        # Check that participants is a list
        assert isinstance(first_activity["participants"], list)

    def test_get_activities_contains_expected_activity_names(self, client):
        """Test that GET /activities returns expected activity names."""
        # Arrange - No special setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()

        # Check for some expected activities
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_returns_correct_participant_counts(self, client):
        """Test that GET /activities returns correct participant counts."""
        # Arrange - No special setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()

        # Check specific activity participant counts
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert chess_club["max_participants"] == 12

        programming_class = activities["Programming Class"]
        assert len(programming_class["participants"]) == 2
        assert programming_class["max_participants"] == 20


class TestPostSignup:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful_adds_participant(self, client):
        """Test successful signup adds participant to activity."""
        # Arrange
        activity_name = "Chess Club"
        new_email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert new_email in result["message"]
        assert activity_name in result["message"]

    def test_signup_actually_modifies_participants_list(self, client):
        """Test that signup actually adds participant to the activity data."""
        # Arrange
        activity_name = "Programming Class"
        new_email = "newstudent@mergington.edu"

        # Get initial count
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={new_email}")
        assert response.status_code == 200

        # Assert - Check that participant was added
        final_response = client.get("/activities")
        final_activities = final_response.json()
        final_count = len(final_activities[activity_name]["participants"])

        assert final_count == initial_count + 1
        assert new_email in final_activities[activity_name]["participants"]

    def test_signup_returns_404_for_nonexistent_activity(self, client):
        """Test that signup returns 404 for activity that doesn't exist."""
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{nonexistent_activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_signup_returns_400_for_already_signed_up_participant(self, client):
        """Test that signup returns 400 when participant is already signed up."""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]

    def test_signup_handles_special_characters_in_email(self, client):
        """Test that signup handles special characters in email addresses."""
        # Arrange
        activity_name = "Gym Class"
        special_email = "test.user+tag@mergington.edu"
        decoded_email = "test.user tag@mergington.edu"  # URL decoding converts + to space

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={special_email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert decoded_email in result["message"]  # FastAPI decodes query params


class TestDeleteUnregister:
    """Test cases for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_successful_removes_participant(self, client):
        """Test successful unregister removes participant from activity."""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={existing_email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert existing_email in result["message"]
        assert activity_name in result["message"]

    def test_unregister_actually_modifies_participants_list(self, client):
        """Test that unregister actually removes participant from the activity data."""
        # Arrange
        activity_name = "Programming Class"
        existing_email = "emma@mergington.edu"

        # Get initial count
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={existing_email}")
        assert response.status_code == 200

        # Assert - Check that participant was removed
        final_response = client.get("/activities")
        final_activities = final_response.json()
        final_count = len(final_activities[activity_name]["participants"])

        assert final_count == initial_count - 1
        assert existing_email not in final_activities[activity_name]["participants"]

    def test_unregister_returns_404_for_nonexistent_activity(self, client):
        """Test that unregister returns 404 for activity that doesn't exist."""
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(f"/activities/{nonexistent_activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_unregister_returns_400_for_not_signed_up_participant(self, client):
        """Test that unregister returns 400 when participant is not signed up."""
        # Arrange
        activity_name = "Chess Club"
        not_signed_up_email = "notsignedup@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={not_signed_up_email}")

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "not signed up" in result["detail"]

    def test_unregister_handles_special_characters_in_email(self, client):
        """Test that unregister handles special characters in email addresses."""
        # Arrange
        activity_name = "Gym Class"
        special_email = "special.user+tag@mergington.edu"
        decoded_email = "special.user tag@mergington.edu"  # URL decoding converts + to space

        # First add the participant
        client.post(f"/activities/{activity_name}/signup?email={special_email}")

        # Act - Now try to remove them
        response = client.delete(f"/activities/{activity_name}/signup?email={special_email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert decoded_email in result["message"]  # FastAPI decodes query params