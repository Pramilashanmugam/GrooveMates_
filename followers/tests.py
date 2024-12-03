from django.contrib.auth.models import User
from .models import Follower
from posts.models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class FollowerListViewTest(APITestCase):
    """
     Tests for the FollowerList view.
    """
    def setUp(self):
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
        Follower.objects.create(
            owner=self.user1,
            followed=self.user2
        )

    def test_can_list_followers(self):
        response = self.client.get('/followers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user_can_follow_other_user(self):
        self.client.login(username='tester1', password='password1')
        response = self.client.post(
            '/followers/', {
                'owner': self.user1.id,
                'followed': self.user3.id,
                }
        )
        count = Follower.objects.count()
        # In the setup a follower relationship was already created, so the
        # count should be 2
        self.assertEqual(count, 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_logged_out_user_cant_follow_other_user(self):
        response = self.client.post(
            '/followers/', {
                'owner': self.user1,
                'followed': self.user3.id,
                }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cant_follow_other_user_twice(self):
        self.client.login(username='tester1', password='password1')
        user1 = User.objects.get(username='tester1')
        user2 = User.objects.get(username='tester2')
        response = self.client.post(
            '/followers/', {'owner': user1, 'followed': user2}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FollowerDetailViewTest(APITestCase):
    """
     Tests for the FollowerDetail view.
    """
    def setUp(self):
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
        self.test_follow = Follower.objects.create(
            owner=self.user1,
            followed=self.user2
        )
        self.test_follow2 = Follower.objects.create(
            owner=self.user2,
            followed=self.user3
        )

    def test_can_retrieve_follower_with_id(self):
        follower_id = self.test_follow.id
        response = self.client.get(f'/followers/{follower_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cant_retrieve_bookmark_using_invalid_id(self):
        response = self.client.get('/followers/2018/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_unfollow_other_user(self):
        self.client.login(username='tester1', password='password1')
        response = self.client.delete('/followers/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cant_delete_folloing_of_other_users(self):
        self.client.login(username='tester1', password='password1')
        response = self.client.delete('/followers/2/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cant_unfollow_other_user_if_not_logged_in(self):
        response = self.client.delete('/followers/1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)