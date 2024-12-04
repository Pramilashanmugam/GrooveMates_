from django.contrib.auth.models import User
from .models import Profile
from rest_framework import status
from rest_framework.test import APITestCase


class ProfileListViewTest(APITestCase):
    """
    Tests for the ProfileList view.
    """
    def setUp(self):
        """
        Create two test users for the profile list tests.
        """
        testuser1 = User.objects.create_user(
            username="testuser1",
            password="password1",
        )
        testuser2 = User.objects.create_user(
            username="testuser2",
            password="password2",
        )

    def test_profile_is_created_automatically(self):
        """
        Ensure profiles are automatically created when users are created.
        """
        # Trigger profile creation through the API
        response = self.client.get('/profiles/')
        self.assertEqual(Profile.objects.count(), 2)

    def test_list_profiles(self):
        """
        Ensure the profile list endpoint returns a 200 OK status.
        """
        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProfileDetailViewTests(APITestCase):
    """
    Tests for the ProfileDetail view.
    """
    def setUp(self):
        """
        Create two test users for profile detail tests.
        """
        testuser1 = User.objects.create_user(
            username="testuser1",
            password="password1",
        )
        testuser2 = User.objects.create_user(
            username="testuser2",
            password="password2",
        )

    def test_can_retrieve_profile_using_valid_id(self):
        """
        Test retrieving a profile with a valid ID returns a 200 OK status.
        """
        response = self.client.get('/profiles/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cant_retrieve_profile_using_invalid_id(self):
        """
        Test retrieving a profile with an invalid ID returns a 404 Not Found
        status.
        """
        response = self.client.get('/profiles/2018/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_logged_in_user_can_update_own_profile(self):
        """
        Test that a logged-in user can update their own profile.
        """
        self.client.login(username='testuser1', password='password1')
        response = self.client.put(
            '/profiles/1/', {'name': 'Testuser 1'}  # Update profile data
        )
        profile = Profile.objects.filter(pk=1).first()
        # Ensure profile name is updated
        self.assertEqual(profile.name, 'Testuser 1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_update_other_users_profile(self):
        """
        Test that a user cannot update another user's profile.
        """
        self.client.login(username='testuser1', password='password1')
        response = self.client.put(
            '/profiles/2/', {'phone_number': '12345'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
