from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Task
from rest_framework_simplejwt.tokens import RefreshToken

class TaskAPITestCase(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.admin_user = User.objects.create_superuser(username="admin", password="adminpass")

        # Create JWT tokens for authentication
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)

        # Sample tasks
        self.task1 = Task.objects.create(title="Task 1", description="Desc 1")
        self.task2 = Task.objects.create(title="Task 2", description="Desc 2", completed=True)

    def test_get_all_tasks(self):
        url = reverse('task-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_task_authenticated(self):
        url = reverse('task-list-create')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {"title": "New Task", "description": "New Desc", "completed": False}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)

    def test_create_task_unauthenticated(self):
        url = reverse('task-list-create')
        data = {"title": "New Task", "description": "New Desc", "completed": False}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_task(self):
        url = reverse('task-put-delete', args=[str(self.task1.id)])
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {"title": "Updated Task"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Updated Task")

    def test_delete_task_as_admin(self):
        url = reverse('task-put-delete', args=[str(self.task1.id)])
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    def test_delete_task_as_non_admin(self):
        url = reverse('task-put-delete', args=[str(self.task2.id)])
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(id=self.task2.id).exists())

    def test_filter_tasks_by_completed(self):
        url = reverse('filter-by-completed', args=['true', 10, 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 1)
