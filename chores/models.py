from django.db import models
from django.utils import timezone


class Chore(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    assigned_member = models.CharField(max_length=100, blank=True, default='')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'title']

    def __str__(self):
        return self.title

    def mark_completed(self, date=None):
        self.status = self.STATUS_COMPLETED
        self.completion_date = date or timezone.now().date()
        self.save()

    def mark_pending(self):
        self.status = self.STATUS_PENDING
        self.completion_date = None
        self.save()
