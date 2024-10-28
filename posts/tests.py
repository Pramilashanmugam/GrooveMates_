from django.contrib.auth.models import User
from django.utils import timezone
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError
from django.urls import reverse


class PostListViewTests(APITestCase):
    """
    Tests for the Post list and creation views.
    """

    def setUp(self):
        """Create a test user for the test cases."""
        self.user = User.objects.create_user(username='adam', password='pass')

    def test_can_list_posts(self):
        """Verify a logged-in user can list posts."""
        Post.objects.create(owner=self.user, event='Sample Event',
                            location='Sample Location')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_logged_in_user_can_create_post(self):
        """Check that a logged-in user can create a post."""
        self.client.login(username='adam', password='pass')
        response = self.client.post('/posts/', {
            'event': 'New Event',
            'location': 'New Location',
            'date': timezone.now().date(),
            'time': timezone.now().time()
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

    def test_user_not_logged_in_cant_create_post(self):
        """Ensure a user must be logged in to create a post."""
        response = self.client.post('/posts/', {
            'event': 'Unauthorized Event',
            'location': 'Unauthorized Location'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_image_filter_choices(self):
        """Validate that image filter choices raise validation errors for
        invalid input."""
        with self.assertRaises(ValidationError):
            post = Post(
                owner=self.user,
                event='Test Event',
                location='Test Location',
                image_filter='invalid_filter'
            )
            post.full_clean()  # Should raise ValidationError

    def test_user_cannot_update_others_post(self):
        """Ensure a user cannot update another user's post."""
        another_user = User.objects.create_user(username='anotheruser',
                                                password='anotherpass')
        post = Post.objects.create(owner=another_user, event='Another Event',
                                   location='Location')
        self.client.login(username='adam', password='pass')
        response = self.client.put(f'/posts/{post.id}/', {
            'event': 'Unauthorized Update',
            'location': 'New Location',
            'date': timezone.now().date(),
            'time': timezone.now().time()
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_others_post(self):
        """Verify that a user cannot delete another user's post."""
        another_user = User.objects.create_user(username='anotheruser',
                                                password='anotherpass')
        post = Post.objects.create(owner=another_user, event='Another Event',
                                   location='Location')
        self.client.login(username='adam', password='pass')
        response = self.client.delete(f'/posts/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)  # Ensure the post exist


class PostDetailTests(APITestCase):
    """
    Tests for the Post detail views, including retrieval, update, and
    delete actions.
    """

    def setUp(self):
        """Create two users and a post for testing."""
        self.owner_user = User.objects.create_user(username='owner',
                                                   password='ownerpass')
        self.other_user = User.objects.create_user(username='other',
                                                   password='otherpass')
        self.post = Post.objects.create(
            owner=self.owner_user,
            event='Test Event',
            description='This is a test event',
            date='2024-10-28',
            time='10:00',
            location='Test Location'
        )
        self.url = reverse('post-detail', kwargs={'pk': self.post.pk})

    def test_get_post_detail_as_owner(self):
        """Verify the owner can retrieve their post's details."""
        self.client.login(username='owner', password='ownerpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['event'], 'Test Event')

    def test_get_post_detail_as_other_user(self):
        """Ensure another user can also retrieve the post's details."""
        self.client.login(username='other', password='otherpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['event'], 'Test Event')

    def test_put_post_as_owner(self):
        """Check that the owner can update their post."""
        self.client.login(username='owner', password='ownerpass')
        updated_data = {
            'event': 'Updated Event',
            'description': 'This is an updated test event',
            'date': '2024-11-01',
            'time': '11:00',
            'location': 'Updated Location'
        }
        response = self.client.put(self.url, updated_data)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.post.event, 'Updated Event')

    def test_put_post_as_other_user(self):
        """Ensure a non-owner cannot update the post."""
        self.client.login(username='other', password='otherpass')
        updated_data = {
            'event': 'Malicious Update',
            'description': 'This should not be allowed',
            'date': '2024-11-01',
            'time': '11:00',
            'location': 'Malicious Location'
        }
        response = self.client.put(self.url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post.refresh_from_db()  # Ensure the post has not been modified
        self.assertEqual(self.post.event, 'Test Event')

    def test_delete_post_as_owner(self):
        """Verify that the owner can delete their post."""
        self.client.login(username='owner', password='ownerpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify post is deleted
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_post_as_other_user(self):
        """Ensure a non-owner cannot delete the post."""
        self.client.login(username='other', password='otherpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Ensure post still exists
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
