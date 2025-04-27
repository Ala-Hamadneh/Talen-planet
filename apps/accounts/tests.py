from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import UserRoles

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        # Create test roles
        self.admin_role = UserRoles.objects.create(role_id=1, role_name="Admin")
        self.buyer_role = UserRoles.objects.create(role_id=2, role_name="Buyer")
        self.seller_role = UserRoles.objects.create(role_id=3, role_name="Seller")
        
        # Create test users
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role_id=self.admin_role.role_id,
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123',
            role_id=self.buyer_role.role_id
        )

    # REGISTRATION TESTS
    def test_user_registration(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'role_id': self.buyer_role.role_id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertFalse(User.objects.last().is_staff)

    def test_admin_registration_by_non_admin(self):
        url = reverse('register')
        data = {
            'username': 'hacker',
            'email': 'hacker@example.com',
            'password': 'hackpass',
            'role_id': self.admin_role.role_id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Only admins can create admin accounts', str(response.data))

    # LOGIN TESTS
    def test_user_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # LOGOUT TESTS
    def test_logout(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('logout')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')

    # USER LIST TESTS
    def test_user_list_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_list_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # USER DETAIL TESTS
    def test_user_detail_own_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_user_detail_other_user_as_regular(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', kwargs={'pk': self.admin.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # PASSWORD CHANGE TESTS
    def test_password_change(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newsecurepass456'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newsecurepass456'))

    def test_password_change_wrong_old_password(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('change-password')
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Wrong password', str(response.data))

    def test_password_change_unauthenticated(self):
        url = reverse('change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)