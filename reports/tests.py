from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from posts.models import Post
from reports.models import Report


class ReportTests(APITestCase):
    """
    Test suite for the Report model, serializers, and views.
    """

    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_superuser(username="admin", password="adminpass")
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")

        # Create a test post
        self.post = Post.objects.create(
            owner=self.user1,
            event="Test Post",
            description="This is a test post."
        )

        # Base URLs for the reports API
        self.report_list_url = '/reports/'
        self.report_detail_url = lambda pk: f'/reports/{pk}/'

    def test_create_report_authenticated_user(self):
        """
        Test that an authenticated user can create a report.
        """
        self.client.login(username="user2", password="password2")
        data = {
            "post": self.post.id,
            "reason": "spam",
            "description": "This post contains spam content."
        }
        response = self.client.post(self.report_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(Report.objects.first().reason, "spam")

    def test_create_report_unauthenticated_user(self):
        """
        Test that an unauthenticated user cannot create a report.
        """
        data = {
            "post": self.post.id,
            "reason": "spam",
            "description": "This post contains spam content."
        }
        response = self.client.post(self.report_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_reports_admin_user(self):
        """
        Test that an admin user can list all reports.
        """
        Report.objects.create(reporter=self.user2, post=self.post, reason="spam")
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.report_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_reports_non_admin_user(self):
        """
        Test that a non-admin user cannot list all reports.
        """
        Report.objects.create(reporter=self.user2, post=self.post, reason="spam")
        self.client.login(username="user1", password="password1")
        response = self.client.get(self.report_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_report_detail_admin_user(self):
        """
        Test that an admin user can retrieve report details.
        """
        report = Report.objects.create(reporter=self.user2, post=self.post, reason="spam")
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.report_detail_url(report.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reason'], "spam")

    def test_update_report_status_admin_user(self):
        """
        Test that an admin user can update a report's status.
        """
        report = Report.objects.create(reporter=self.user2, post=self.post, reason="spam")
        self.client.login(username="admin", password="adminpass")
        data = {"status": "Reviewed"}
        response = self.client.patch(self.report_detail_url(report.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Report.objects.first().status, "Reviewed")

    def test_update_report_status_non_admin_user(self):
        """
        Test that a non-admin user cannot update a report's status.
        """
        report = Report.objects.create(reporter=self.user2, post=self.post, reason="spam")
        self.client.login(username="user2", password="password2")
        data = {"status": "Reviewed"}
        response = self.client.patch(self.report_detail_url(report.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_report_admin_user(self):
        """
        Test that an admin user can delete a report.
        """
        report = Report.objects.create(reporter=self.user2, post=self.post, reason="spam")
        self.client.login(username="admin", password="adminpass")
        response = self.client.delete(self.report_detail_url(report.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Report.objects.count(), 0)

    def test_delete_report_non_admin_user(self):
        """
        Test that a non-admin user cannot delete a report.
        """
        report = Report.objects.create(reporter=self.user2, post=self.post, reason="spam")
        self.client.login(username="user2", password="password2")
        response = self.client.delete(self.report_detail_url(report.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Report.objects.count(), 1)
