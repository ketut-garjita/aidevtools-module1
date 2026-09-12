from django.contrib import admin
from .models import Chore


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'assigned_member',
        'due_date',
        'status',
        'completion_date',
        'created_at',
    )
    list_filter = ('status', 'due_date', 'completion_date', 'assigned_member')
    search_fields = ('title', 'description', 'assigned_member')
    date_hierarchy = 'due_date'
    ordering = ('due_date', 'title')

    actions = ['mark_as_completed', 'mark_as_pending']

    @admin.action(description='Mark selected chores as completed')
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(
            status=Chore.STATUS_COMPLETED,
            completion_date=timezone.now().date()
        )

    @admin.action(description='Mark selected chores as pending')
    def mark_as_pending(self, request, queryset):
        queryset.update(
            status=Chore.STATUS_PENDING,
            completion_date=None
        )
