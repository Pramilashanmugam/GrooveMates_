from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from posts.models import Post
from likes.models import Like


class LikeTests(APITestCase):
    """
    Test suite for the Like model, serializers, and views.
    """

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

        # Create a test post
        self.post = Post.objects.create(
            owner=self.user1,
            event="Test Post",
            description="This is a test post."
        )

        # Base URL for the Like API
        self.like_list_url = '/likes/'
        self.like_detail_url = lambda pk: f'/likes/{pk}/'

    def test_create_like_authenticated_user(self):
        """
        Test that an authenticated user can like a post.
        """
        self.client.login(username='user2', password='password2')
        response = self.client.post(self.like_list_url, {'post': self.post.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(Like.objects.first().owner, self.user2)

    def test_create_like_unauthenticated_user(self):
        """
        Test that an unauthenticated user cannot like a post.
        """
        response = self.client.post(self.like_list_url, {'post': self.post.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_like_list(self):
        """
        Test that the list of likes can be retrieved by any user.
        """
        Like.objects.create(owner=self.user1, post=self.post)
        response = self.client.get(self.like_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_like_detail(self):
        """
        Test that the details of a specific like can be retrieved.
        """
        like = Like.objects.create(owner=self.user1, post=self.post)
        response = self.client.get(self.like_detail_url(like.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner'], self.user1.username)

    def test_delete_like_owner(self):
        """
        Test that the owner of a like can delete it.
        """
        self.client.login(username='user1', password='password1')
        like = Like.objects.create(owner=self.user1, post=self.post)
        response = self.client.delete(self.like_detail_url(like.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.count(), 0)

    def test_delete_like_non_owner(self):
        """
        Test that a non-owner cannot delete a like.
        """
        self.client.login(username='user2', password='password2')
        like = Like.objects.create(owner=self.user1, post=self.post)
        response = self.client.delete(self.like_detail_url(like.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 1)

    def test_unique_constraint_on_like(self):
        """
        Test that a user cannot like the same post more than once.
        """
        self.client.login(username='user1', password='password1')
        Like.objects.create(owner=self.user1, post=self.post)
        response = self.client.post(self.like_list_url, {'post': self.post.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('possible duplicate', response.data['detail'])
