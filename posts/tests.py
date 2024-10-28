from django.contrib.auth.models import User
from django.utils import timezone
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError


class PostListViewTests(APITestCase):
    """
    Test case for the Post list and creation views.

    This test suite covers the following scenarios:
    - Listing posts by logged-in users.
    - Creating posts by logged-in users.
    - Ensuring that users must be logged in to create posts.
    - Validating image filter choices when creating a post.
    """

    def setUp(self):
        """Set up the test case with a user instance."""
        self.user = User.objects.create_user(username='adam', password='pass')

    def test_can_list_posts(self):
        """Test that a logged-in user can list posts."""
        Post.objects.create(owner=self.user, event='Sample Event', location='Sample Location')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_logged_in_user_can_create_post(self):
        """Test that a logged-in user can create a post."""
        self.client.login(username='adam', password='pass')
        
        response = self.client.post('/posts/', {
            'event': 'New Event',
            'location': 'New Location',
            'date': timezone.now().date(),
            'time': timezone.now().time()
        })

        # Debug response data
        print("Response data:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

    def test_user_not_logged_in_cant_create_post(self):
        """Test that a user must be logged in to create a post."""
        response = self.client.post('/posts/', {
            'event': 'Unauthorized Event',
            'location': 'Unauthorized Location'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_image_filter_choices(self):
        """Test validation for image filter choices."""
        with self.assertRaises(ValidationError):
            post = Post(
                owner=self.user,
                event='Test Event',
                location='Test Location',
                image_filter='invalid_filter'  # Invalid choice
            )
            post.full_clean()  # Should raise ValidationError
    
    def test_user_cannot_update_others_post(self):
        """Test that a user cannot update another user's post."""
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
        """Test that a user cannot delete another user's post."""
        another_user = User.objects.create_user(username='anotheruser',
                                                password='anotherpass')
        post = Post.objects.create(owner=another_user, event='Another Event',
                                location='Location')

        self.client.login(username='adam', password='pass')
        response = self.client.delete(f'/posts/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)  # Ensure the post still exists

