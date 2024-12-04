from django.contrib.auth.models import User
from .models import Follower
from posts.models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class FollowerListViewTest(APITestCase):
    """
    Tests for the FollowerList view, which handles the creation and
    listing of followers.
    """

    def setUp(self):
        """
        Set up the test environment:
        - Create three users: user1, user2, and user3.
        - Create a follower relationship between user1 and user2.
        """
        self.user1 = User.objects.create_user(
            username="tester1",
            password="password1",
        )
        self.user2 = User.objects.create_user(
            username="tester2",
            password="password2",
        )
        self.user3 = User.objects.create_user(
            username="tester3",
            password="password3"
        )
        # user1 follows user2
        Follower.objects.create(
            owner=self.user1,
            followed=self.user2
        )

    def test_can_list_followers(self):
        """
        Test that the list of followers can be retrieved by any user.
        Verifies that the follower list returns a successful response.
        """
        response = self.client.get('/followers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user_can_follow_other_user(self):
        """
        Test that a logged-in user can follow another user.
        Verifies that the follower count increases and the correct status code
        is returned.
        """
        self.client.login(username='tester1', password='password1')
        response = self.client.post(
            '/followers/', {
                'owner': self.user1.id,
                'followed': self.user3.id,
            }
        )
        # Verify that the number of followers increases by 1
        count = Follower.objects.count()
        self.assertEqual(count, 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_logged_out_user_cant_follow_other_user(self):
        """
        Test that an unauthenticated user cannot follow another user.
        Verifies that the server returns a 403 Forbidden status.
        """
        response = self.client.post(
            '/followers/', {
                'owner': self.user1.id,
                'followed': self.user3.id,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cant_follow_other_user_twice(self):
        """
        Test that a user cannot follow another user more than once.
        Verifies that trying to create a duplicate follow relationship
        returns a 400 Bad Request status.
        """
        self.client.login(username='tester1', password='password1')
        user1 = User.objects.get(username='tester1')
        user2 = User.objects.get(username='tester2')
        response = self.client.post(
            '/followers/', {'owner': user1, 'followed': user2}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FollowerDetailViewTest(APITestCase):
    """
    Tests for the FollowerDetail view, which handles the retrieval and deletion
    of specific follower relationships.
    """

    def setUp(self):
        """
        Set up the test environment:
        - Create three users: user1, user2, and user3.
        - Create two follower relationships:
            - user1 follows user2
            - user2 follows user3
        """
        self.user1 = User.objects.create_user(
            username="tester1",
            password="password1",
        )
        self.user2 = User.objects.create_user(
            username="tester2",
            password="password2",
        )
        self.user3 = User.objects.create_user(
            username="tester3",
            password="password3"
        )
        # Follower relationships
        self.test_follow = Follower.objects.create(
            owner=self.user1,
            followed=self.user2
        )
        self.test_follow2 = Follower.objects.create(
            owner=self.user2,
            followed=self.user3
        )

    def test_can_retrieve_follower_with_id(self):
        """
        Test that a follower relationship can be retrieved by its ID.
        Verifies that the correct follower details are returned.
        """
        follower_id = self.test_follow.id
        response = self.client.get(f'/followers/{follower_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cant_retrieve_follower_using_invalid_id(self):
        """
        Test that an invalid follower ID results in a 404 Not Found error.
        Verifies that trying to retrieve a non-existent follower returns the
        correct error.
        """
        response = self.client.get('/followers/2018/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_unfollow_other_user(self):
        """
        Test that a logged-in user can unfollow another user.
        Verifies that the unfollow action successfully deletes the follower
        relationship.
        """
        self.client.login(username='tester1', password='password1')
        response = self.client.delete('/followers/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cant_delete_following_of_other_users(self):
        """
        Test that a user cannot delete a follow relationship that they do not
        own.
        Verifies that only the owner of the follower relationship can delete it
        """
        self.client.login(username='tester1', password='password1')
        response = self.client.delete('/followers/2/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cant_unfollow_other_user_if_not_logged_in(self):
        """
        Test that a user cannot unfollow another user if they are not logged in
        Verifies that an unauthenticated request to unfollow results in a
        forbidden error.
        """
        response = self.client.delete('/followers/1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
