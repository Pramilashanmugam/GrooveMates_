from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from posts.models import Post
from likes.models import Like


class LikeTests(APITestCase):
    """
    Test suite for the Like model, serializers, and views.
    Includes tests for creating, retrieving, and deleting likes.
    Ensures correct behavior when the user is authenticated or unauthenticated,
    and verifies constraints like liking the same post multiple times.
    """

    def setUp(self):
        """
        Set up the test environment:
        - Create two users.
        - Create a post associated with user1.
        """
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1', password='password1'
            )
        self.user2 = User.objects.create_user(
            username='user2', password='password2'
            )

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
        Verifies that a like is created and associated with the correct user.
        """
        self.client.login(username='user2', password='password2')
        response = self.client.post(self.like_list_url, {'post': self.post.id})
        # Ensure the status code indicates successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Ensure a Like object is created
        self.assertEqual(Like.objects.count(), 1)
        # Ensure the Like object is associated with the correct user
        self.assertEqual(Like.objects.first().owner, self.user2)

    def test_create_like_unauthenticated_user(self):
        """
        Test that an unauthenticated user cannot like a post.
        Verifies that the server returns a forbidden status for unauthenticated
        requests.
        """
        response = self.client.post(self.like_list_url, {'post': self.post.id})
        # Expecting HTTP 403 Forbidden for unauthenticated users
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_like_list(self):
        """
        Test that the list of likes can be retrieved by any user.
        Verifies that the list includes the expected likes.
        """
        # Create a like for user1
        Like.objects.create(owner=self.user1, post=self.post)
        response = self.client.get(self.like_list_url)
        # Ensure the response status is OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure the list contains exactly 1 like
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_like_detail(self):
        """
        Test that the details of a specific like can be retrieved.
        Verifies that the correct like details are returned.
        """
        # Create a like for user1
        like = Like.objects.create(owner=self.user1, post=self.post)
        response = self.client.get(self.like_detail_url(like.id))
        # Ensure the response status is OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure the response includes the correct owner
        self.assertEqual(response.data['owner'], self.user1.username)

    def test_delete_like_owner(self):
        """
        Test that the owner of a like can delete it.
        Verifies that the like is deleted and no longer exists.
        """
        self.client.login(username='user1', password='password1')
        # Create a like for user1
        like = Like.objects.create(owner=self.user1, post=self.post)
        response = self.client.delete(self.like_detail_url(like.id))
        # Ensure the response indicates successful deletion
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Ensure the Like object is deleted
        self.assertEqual(Like.objects.count(), 0)

    def test_delete_like_non_owner(self):
        """
        Test that a non-owner cannot delete a like.
        Verifies that only the like's owner can delete it.
        """
        self.client.login(username='user2', password='password2')
        # Create a like for user1
        like = Like.objects.create(owner=self.user1, post=self.post)
        response = self.client.delete(self.like_detail_url(like.id))
        # Ensure the response indicates forbidden action for non-owners
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Ensure the Like object is still present
        self.assertEqual(Like.objects.count(), 1)

    def test_unique_constraint_on_like(self):
        """
        Test that a user cannot like the same post more than once.
        Verifies that duplicate likes are prevented with a 400 Bad Request.
        """
        self.client.login(username='user1', password='password1')
        # User1 likes the post
        Like.objects.create(owner=self.user1, post=self.post)
        # Attempt to like the same post again
        response = self.client.post(self.like_list_url, {'post': self.post.id})
        # Ensure the response indicates a bad request due to duplicate like
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure the error message contains 'possible duplicate'
        self.assertIn('possible duplicate', response.data['detail'])
