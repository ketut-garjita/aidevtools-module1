from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.admin.sites import site
from .models import Chore
from .admin import ChoreAdmin


class ChoreModelTest(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.chore = Chore.objects.create(
            title='Wash dishes',
            description='Wash and dry all cookware in sink',
            assigned_member='Alice',
            due_date=self.today + timedelta(days=1),
            status=Chore.STATUS_PENDING
        )

    def test_chore_creation(self):
        """Test creating a chore and field values."""
        self.assertEqual(self.chore.title, 'Wash dishes')
        self.assertEqual(self.chore.description, 'Wash and dry all cookware in sink')
        self.assertEqual(self.chore.assigned_member, 'Alice')
        self.assertEqual(self.chore.status, Chore.STATUS_PENDING)
        self.assertIsNone(self.chore.completion_date)

    def test_chore_str(self):
        """Test the string representation of a chore."""
        self.assertEqual(str(self.chore), 'Wash dishes')

    def test_mark_completed_method(self):
        """Test mark_completed helper method."""
        self.chore.mark_completed()
        self.chore.refresh_from_db()
        self.assertEqual(self.chore.status, Chore.STATUS_COMPLETED)
        self.assertEqual(self.chore.completion_date, self.today)

    def test_mark_pending_method(self):
        """Test mark_pending helper method resets completion date."""
        self.chore.mark_completed()
        self.chore.mark_pending()
        self.chore.refresh_from_db()
        self.assertEqual(self.chore.status, Chore.STATUS_PENDING)
        self.assertIsNone(self.chore.completion_date)


class ChoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.today = timezone.now().date()
        self.chore1 = Chore.objects.create(
            title='Clean kitchen',
            assigned_member='Bob',
            due_date=self.today,
            status=Chore.STATUS_PENDING
        )
        self.chore2 = Chore.objects.create(
            title='Mop hallway',
            assigned_member='Charlie',
            due_date=self.today - timedelta(days=2),
            status=Chore.STATUS_COMPLETED,
            completion_date=self.today - timedelta(days=1)
        )

    def test_chore_list_view(self):
        """Test chore list page loads with chores."""
        response = self.client.get(reverse('chores:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chores/chore_list.html')
        self.assertContains(response, 'Clean kitchen')
        self.assertContains(response, 'Mop hallway')
        self.assertEqual(response.context['total_count'], 2)
        self.assertEqual(response.context['pending_count'], 1)
        self.assertEqual(response.context['completed_count'], 1)

    def test_chore_list_filter_status(self):
        """Test filtering chores by status."""
        response = self.client.get(reverse('chores:list'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clean kitchen')
        self.assertNotContains(response, 'Mop hallway')

    def test_chore_list_filter_member(self):
        """Test filtering chores by assigned member."""
        response = self.client.get(reverse('chores:list'), {'member': 'Bob'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clean kitchen')
        self.assertNotContains(response, 'Mop hallway')

    def test_chore_create_get(self):
        """Test chore create GET page loads."""
        response = self.client.get(reverse('chores:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chores/chore_form.html')

    def test_chore_create_post_success(self):
        """Test creating a chore via POST."""
        post_data = {
            'title': 'Take out recycling',
            'description': 'Blue bins by the curbside',
            'assigned_member': 'Diana',
            'due_date': self.today.strftime('%Y-%m-%d'),
            'status': Chore.STATUS_PENDING,
        }
        response = self.client.post(reverse('chores:create'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('chores:list'))

        new_chore = Chore.objects.get(title='Take out recycling')
        self.assertEqual(new_chore.assigned_member, 'Diana')
        self.assertEqual(new_chore.status, Chore.STATUS_PENDING)

    def test_chore_complete_action(self):
        """Test marking a chore completed."""
        self.assertEqual(self.chore1.status, Chore.STATUS_PENDING)
        response = self.client.post(reverse('chores:complete', args=[self.chore1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('chores:list'))

        self.chore1.refresh_from_db()
        self.assertEqual(self.chore1.status, Chore.STATUS_COMPLETED)
        self.assertEqual(self.chore1.completion_date, self.today)

    def test_chore_delete_action(self):
        """Test deleting a chore."""
        response = self.client.post(reverse('chores:delete', args=[self.chore1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Chore.objects.filter(id=self.chore1.id).exists())


class ChoreAdminTest(TestCase):
    def test_admin_registration(self):
        """Test Chore model is registered in admin site."""
        self.assertIn(Chore, site._registry)
        self.assertIsInstance(site._registry[Chore], ChoreAdmin)
