from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from posts.models import Post
from shares.models import Share


class ShareTests(TestCase):
    def setUp(self):
        """
        Set up test data for the Share API.
        """
        self.client = APIClient()
        
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        
        # Create posts
        self.post1 = Post.objects.create(owner=self.user1, event="Test Event 1", location="Location 1")
        self.post2 = Post.objects.create(owner=self.user2, event="Test Event 2", location="Location 2")
        
        # Authenticate user1
        self.client.login(username="user1", password="password123")
        
        # Create a share
        self.share1 = Share.objects.create(user=self.user1, post=self.post2)

    def test_list_shares(self):
        response = self.client.get('/shares/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data["results"][0])
        self.assertIn("user", response.data["results"][0])
        self.assertIn("post", response.data["results"][0])

    def test_create_duplicate_share(self):
        data = {"post": self.post2.id}
        response = self.client.post('/shares/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You have already shared this post.", str(response.data))


    def test_list_shared_posts(self):
        response = self.client.get('/shared-posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.post2.id)

    def test_list_shared_posts_by_profile_id(self):
        profile_id = self.user1.profile.id
        response = self.client.get(f'/shared-posts/?profile_id={profile_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.post2.id)


    def test_unauthenticated_user_access(self):
        """
        Test that unauthenticated users cannot create shares.
        """
        self.client.logout()
        data = {"post": self.post1.id}
        response = self.client.post('/shares/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

