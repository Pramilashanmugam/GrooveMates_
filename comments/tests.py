from django.contrib.auth.models import User
from .models import Comment
from posts.models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class CommentListViewTest(APITestCase):
    """
    Tests for the CommentList view, which handles listing and creating comments
    """

    def setUp(self):
        """
        Set up the test environment:
        - Create a test user.
        - Create a test post associated with the test user.
        """
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
        """
        Test that comments can be listed successfully.
        Verifies that the API returns a 200 OK status when listing comments.
        """
        # Create a comment for the test post
        Comment.objects.create(
            owner=self.tester,
            post=self.test_post,
            description="A test comment",
        )
        response = self.client.get("/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user_can_create_comment(self):
        """
        Test that a logged-in user can create a comment.
        Verifies that a comment is created and the API returns a 201 CREATED
        status.
        """
        self.client.login(username="tester", password="password")
        response = self.client.post(
            "/comments/",
            {
                "post": self.test_post.id,
                "description": "A test comment",
            },
        )
        count = Comment.objects.count()
        self.assertEqual(count, 1)  # Ensure comment count increased
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_logged_out_user_cant_create_comment(self):
        """
        Test that a logged-out user cannot create a comment.
        Verifies that an unauthenticated user is forbidden to create a comment.
        """
        response = self.client.post(
            "/comments/",
            {
                "post": self.test_post.id,
                "description": "A test comment",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentDetailViewTest(APITestCase):
    """
    Tests for the CommentDetail view, which handles retrieving, updating,
    and deleting comments.
    """

    def setUp(self):
        """
        Set up the test environment:
        - Create two test users.
        - Create two posts, each owned by different users.
        - Create two comments, one for each post.
        """
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
        # Create comments for different posts
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
        """
        Test that a comment can be retrieved by its ID.
        Verifies that the API correctly returns the comment details when the
        comment ID is valid.
        """
        response = self.client.get("/comments/1/")
        # Check if the comment's description matches the expected value
        self.assertEqual(response.data["description"], "Nice post tester 2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cant_retrieve_comment_using_invalid_id(self):
        """
        Test that attempting to retrieve a comment using an invalid ID results
        in a 404 Not Found error.
        """
        response = self.client.get("/comments/2018/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_comment(self):
        """
        Test that a logged-in user can update their own comment.
        Verifies that the comment's description is successfully updated.
        """
        self.client.login(username="tester1", password="password1")
        response = self.client.put(
            "/comments/1/",
            {
                "description": "Really nice post tester 2",
            },
        )
        # Ensure the comment was updated in the database
        comment = Comment.objects.filter(pk=1).first()
        self.assertEqual(comment.description, "Really nice post tester 2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_update_other_users_comment(self):
        """
        Test that a user cannot update a comment they do not own.
        Verifies that the API returns a 403 Forbidden status when trying to
        edit another user's comment.
        """
        self.client.login(username="tester1", password="password1")
        response = self.client.put(
            "/comments/2/",
            {
                "description": "Post looks bad tester 1",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_delete_own_comment(self):
        """
        Test that a logged-in user can delete their own comment.
        Verifies that the comment is deleted and the API returns a 204
        NO CONTENT status.
        """
        self.client.login(username="tester1", password="password1")
        response = self.client.delete("/comments/1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cant_delete_other_users_comment(self):
        """
        Test that a user cannot delete a comment they do not own.
        Verifies that the API returns a 403 Forbidden status when trying to
        delete another user's comment.
        """
        self.client.login(username="tester1", password="password1")
        response = self.client.delete("/comments/2/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
