from django.contrib.auth.models import User
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class PostListViewTest(APITestCase):
    """
    Tests for the PostList view.
    Covers listing posts, creating a post as a logged-in user,
    and restrictions for logged-out users.
    """

    def setUp(self):
        """
        Create a test user for authentication.
        """
        self.user = User.objects.create_user(
            username="tester",
            password="password",
        )

    def test_can_list_posts(self):
        """
        Ensure the endpoint returns a 200 status code for listing posts.
        """
        self.client.login(username='tester', password='password')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user_can_create_post(self):
        """
        Ensure a logged-in user can create a post and the post count increases.
        """
        self.client.login(username='tester', password='password')
        response = self.client.post(
            '/posts/', {
                'event': 'post event',
                'date': '2025-07-29',
                'time': '14:00:00',
                'location': 'Test location',
                'image': '',
                'description': 'Test description',
            }
        )
        count = Post.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_logged_out_user_cant_create_post(self):
        """
        Ensure a logged-out user cannot create a post (403 Forbidden).
        """
        response = self.client.post(
            '/posts/', {
                'event': 'post event',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PostDetailViewTest(APITestCase):
    """
    Tests for the PostDetail view.
    Covers retrieving, updating, and deleting posts with permission constraints
    """

    def setUp(self):
        """
        Create two test users and two posts, one for each user.
        """
        tester1 = User.objects.create_user(
            username="tester1",
            password="password1",
        )
        tester2 = User.objects.create_user(
            username="tester2",
            password="password2",
        )
        Post.objects.create(
            owner=tester1,
            event='Post event tester1',
            date='2025-08-01',
            time='15:00:00',
            location='Test location tester1',
            description='Test description 1',
        )
        Post.objects.create(
            owner=tester2,
            event='Post event tester2',
            date='2025-08-03',
            time='09:00:00',
            location='Test location tester2',
            description='Test description 2',
        )

    def test_can_retrieve_post_with_id(self):
        """
        Ensure a logged-in user can retrieve a post by its ID.
        """
        self.client.login(username='tester1', password='password1')
        response = self.client.get('/posts/1/')
        self.assertEqual(
            response.data['event'], 'Post event tester1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cant_retrieve_post_using_invalid_id(self):
        """
        Ensure retrieving a post with an invalid ID returns 404 Not Found.
        """
        response = self.client.get('/posts/2018/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_post(self):
        """
        Ensure a logged-in user can update their own post.
        """
        self.client.login(username='tester1', password='password1')
        response = self.client.put('/posts/1/', {
            'event': 'post update event',
            'date': '2025-08-01',
            'time': '15:00:00',
            'location': 'Test location tester1',
        })
        post = Post.objects.filter(pk=1).first()
        self.assertEqual(post.event, 'post update event')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_update_other_users_post(self):
        """
        Ensure a user cannot update another user's post (403 Forbidden).
        """
        self.client.login(username='tester1', password='password1')
        response = self.client.put('/posts/2/', {
            'event': 'post update event 2',
            'date': '2025-08-03',
            'time': '09:00:00',
            'location': 'Test location tester2',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_delete_own_post(self):
        """
        Ensure a user can delete their own post.
        """
        self.client.login(username='tester1', password='password1')
        response = self.client.delete('/posts/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cant_delete_other_users_post(self):
        """
        Ensure a user cannot delete another user's post (403 Forbidden).
        """
        self.client.login(username='tester1', password='password1')
        response = self.client.delete('/posts/2/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
