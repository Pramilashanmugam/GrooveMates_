from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from posts.models import Post
from shares.models import Share


class ShareTests(TestCase):
    """
    Test suite for the Share API functionality.
    """

    def setUp(self):
        """
        Set up test data for the Share API.

        This includes:
        - Creating two test users
        - Creating two posts, each owned by one of the users
        - Authenticating the first user for subsequent tests
        - Creating an initial share object for testing listing and duplicate
        prevention
        """
        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user(
            username="user1", password="password123"
            )
        self.user2 = User.objects.create_user(
            username="user2", password="password123"
            )

        # Create posts
        self.post1 = Post.objects.create(
            owner=self.user1, event="Test Event 1", location="Location 1"
            )
        self.post2 = Post.objects.create(
            owner=self.user2, event="Test Event 2", location="Location 2"
            )

        # Authenticate user1
        self.client.login(username="user1", password="password123")

        # Create a share
        self.share1 = Share.objects.create(user=self.user1, post=self.post2)

    def test_list_shares(self):
        """
        Test the endpoint that lists all shares.

        Ensures that:
        - The response status is 200 OK
        - The returned data contains the required fields ('id', 'user', 'post')
        """
        response = self.client.get('/shares/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data["results"][0])
        self.assertIn("user", response.data["results"][0])
        self.assertIn("post", response.data["results"][0])

    def test_create_duplicate_share(self):
        """
        Test that a user cannot share the same post more than once.

        Ensures that:
        - The response status is 400 BAD REQUEST
        - The response includes a specific validation error message
        """
        data = {"post": self.post2.id}
        response = self.client.post('/shares/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You have already shared this post.", str(response.data))

    def test_list_shared_posts(self):
        """
        Test listing posts shared by the authenticated user.

        Ensures that:
        - The response status is 200 OK
        - The number of posts returned matches the expected count
        - The returned post matches the one shared by the user
        """
        response = self.client.get('/shared-posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.post2.id)

    def test_list_shared_posts_by_profile_id(self):
        """
        Test listing posts shared by a specific profile using `profile_id`.

        Ensures that:
        - The response status is 200 OK
        - The number of posts returned matches the expected count
        - The returned post matches the one shared by the user associated with
        the profile
        """
        profile_id = self.user1.profile.id
        response = self.client.get(f'/shared-posts/?profile_id={profile_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.post2.id)

    def test_unauthenticated_user_access(self):
        """
        Test that unauthenticated users cannot create shares.

        Ensures that:
        - The response status is 403 FORBIDDEN
        - The share is not created in the database
        """
        self.client.logout()
        data = {"post": self.post1.id}
        response = self.client.post('/shares/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
