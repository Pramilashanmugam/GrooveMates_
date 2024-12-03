from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing Report model in the Django admin
    interface.
    This class customizes the admin view for the Report model, including:
    - Displaying specific fields in the list view.
    - Adding filters to easily filter reports by status, reason, or creation
    date.
    - Enabling search functionality for certain fields to allow efficient
    searching.

    Attributes:
        list_display (tuple): The fields to display in the list view for
        reports.
        list_filter (tuple): The fields that can be used as filters in the
        admin interface.
        search_fields (tuple): The fields to enable searching within the
        report list view.
    """

    # Fields to display in the list view for each Report instance
    list_display = ('reporter', 'post', 'reason', 'status', 'created_at')

    # Filters to apply in the right sidebar for filtering reports
    list_filter = ('status', 'reason', 'created_at')

    # Fields that can be searched through the search bar in the admin view
    search_fields = ('reporter__username', 'post__title', 'description')
