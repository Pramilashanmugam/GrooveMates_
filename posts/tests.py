from django.contrib.auth.models import User
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError
from django.utils import timezone


class PostListViewTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='adam', password='pass')

    def test_can_list_posts(self):
        # Create a post with required fields only
        Post.objects.create(owner=self.user, event='Sample Event', location='Sample Location')
        
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Optional: Print response data for debugging (remove or comment out in production)
        print(response.data)
        print(len(response.data))
        
        # Assert that one post is returned in the response data
        self.assertEqual(len(response.data), 1)

    def test_logged_in_user_can_create_post(self):
        # Log in the test user
        self.client.login(username='adam', password='pass')
        
        # Post request with required fields
        response = self.client.post('/posts/', {
        'event': 'New Event',
        'location': 'New Location',
        'date': timezone.now().date(),
        'time': timezone.now().time()
    })
        # Print the response data for debugging
        print(response.data)
            
        # Check the count and status code
        count = Post.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_not_logged_in_cant_create_post(self):
        # Attempt to create a post without logging in
        response = self.client.post('/posts/', {
            'event': 'Unauthorized Event',
            'location': 'Unauthorized Location'
        })
        
        # Ensure the status code is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_image_filter_choices(self):
        with self.assertRaises(ValidationError):
            post = Post(
                owner=self.user,
                event='Test Event',
                location='Test Location',
                image_filter='invalid_filter'  # An invalid choice
            )
            post.full_clean()  # This will raise a ValidationError due to the invalid choice