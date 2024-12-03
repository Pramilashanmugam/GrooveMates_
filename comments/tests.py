from django.contrib.auth.models import User
from .models import Comment
from posts.models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class CommentListViewTest(APITestCase):
    """
    Tests for the CommentList view.
    """

    def setUp(self):
        self.tester = User.objects.create_user(
            username="tester",
            password="password",
        )
        self.test_post = Post.objects.create(
            owner=self.tester,
            event="post event",
            date="2024-08-29",
            time="14:00:00",
        )

    def test_can_list_comments(self):
        Comment.objects.create(
            owner=self.tester,
            post=self.test_post,
            description="A test comment",
        )
        response = self.client.get("/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user_can_create_comment(self):
        self.client.login(username="tester", password="password")
        response = self.client.post(
            "/comments/",
            {
                "post": self.test_post.id,
                "description": "A test comment",
            },
        )
        count = Comment.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_logged_out_user_cant_create_comment(self):
        response = self.client.post(
            "/comments/",
            {
                "comment": "post event",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentDetailViewTest(APITestCase):
    """
    Tests for the CommentDetail view.
    """

    def setUp(self):
        tester1 = User.objects.create_user(
            username="tester1",
            password="password1",
        )
        tester2 = User.objects.create_user(
            username="tester2",
            password="password2",
        )
        test_post1 = Post.objects.create(
            owner=tester1,
            event="post event tester1",
            date="2024-09-01",
            time="15:00:00",
            location="Test location tester1",
            description="Test description 1",
            )
        test_post2 = Post.objects.create(
            owner=tester2,
            event="post event tester2",
            date="2024-09-03",
            time="09:00:00",
            location="Test location tester2",
            description="Test description 2",
        )
        test_comment1 = Comment.objects.create(
            owner=tester1,
            post=test_post2,
            description="Nice post tester 2",
        )
        test_comment2 = Comment.objects.create(
            owner=tester2,
            post=test_post1,
            description="Good post tester 1",
        )

    def test_can_retrieve_comment_with_id(self):
        response = self.client.get("/comments/1/")
        self.assertEqual(
            response.data["description"], "Nice post tester 2"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cant_retrieve_comment_using_invalid_id(self):
        response = self.client.get("/comments/2018/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_comment(self):
        self.client.login(username="tester1", password="password1")
        response = self.client.put(
            "/comments/1/",
            {
                "description": "Really nice post tester 2",
            },
        )
        comment = Comment.objects.filter(pk=1).first()
        self.assertEqual(
            comment.description, "Really nice post tester 2"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_update_other_users_comment(self):
        self.client.login(username="tester1", password="password1")
        response = self.client.put(
            "/comments/2/",
            {
                "description": "Post looks bad tester 1",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_delete_own_comment(self):
        self.client.login(username="tester1", password="password1")
        response = self.client.delete("/comments/1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cant_delete_other_users_comment(self):
        self.client.login(username="tester1", password="password1")
        response = self.client.delete("/comments/2/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)