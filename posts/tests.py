from django.contrib.auth.models import User
from django.utils import timezone
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError


class PostListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='adam', password='pass')

    def test_can_list_posts(self):
        Post.objects.create(owner=self.user, event='Sample Event', location='Sample Location')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_logged_in_user_can_create_post(self):
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
        response = self.client.post('/posts/', {
            'event': 'Unauthorized Event',
            'location': 'Unauthorized Location'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_image_filter_choices(self):
        with self.assertRaises(ValidationError):
            post = Post(
                owner=self.user,
                event='Test Event',
                location='Test Location',
                image_filter='invalid_filter'  # Invalid choice
            )
            post.full_clean()  # Should raise ValidationError
