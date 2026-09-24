from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import Profile, User


class AuthApiTests(APITestCase):
    def create_user(self, username, user_type, password='Testpass123!'):
        user = User.objects.create_user(
            username=username,
            password=password,
            type=user_type,
            email=f'{username}@example.com',
        )
        Profile.objects.create(user=user)
        return user

    def test_registration_creates_user_profile_and_token(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Testpass123!',
            'repeated_password': 'Testpass123!',
            'type': User.CUSTOMER,
        }
        response = self.client.post('/api/registration/', data, format='json')
        user = User.objects.get(username='newuser')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password('Testpass123!'))
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertIn('token', response.data)

    def test_registration_rejects_password_mismatch(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Testpass123!',
            'repeated_password': 'Wrongpass123!',
            'type': User.CUSTOMER,
        }
        response = self.client.post('/api/registration/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_token(self):
        self.create_user('customer', User.CUSTOMER)
        data = {'username': 'customer', 'password': 'Testpass123!'}
        response = self.client.post('/api/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer')
        self.assertIn('token', response.data)

    def test_login_rejects_invalid_credentials(self):
        self.create_user('customer', User.CUSTOMER)
        data = {'username': 'customer', 'password': 'wrong'}
        response = self.client.post('/api/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_requires_authentication(self):
        user = self.create_user('customer', User.CUSTOMER)
        response = self.client.get(f'/api/profile/{user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_read_profile(self):
        user = self.create_user('customer', User.CUSTOMER)
        self.client.force_authenticate(user=user)
        response = self.client.get(f'/api/profile/{user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], user.username)

    def test_user_can_update_own_profile(self):
        user = self.create_user('customer', User.CUSTOMER)
        self.client.force_authenticate(user=user)
        data = {'first_name': 'Etem', 'location': 'Cologne'}
        response = self.client.patch(
            f'/api/profile/{user.id}/', data, format='json'
        )
        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.first_name, 'Etem')
        self.assertEqual(user.profile.location, 'Cologne')

    def test_user_cannot_update_another_profile(self):
        user = self.create_user('customer', User.CUSTOMER)
        other = self.create_user('other', User.CUSTOMER)
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            f'/api/profile/{other.id}/', {'location': 'Berlin'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_profile_lists_are_filtered_by_type(self):
        customer = self.create_user('customer', User.CUSTOMER)
        business = self.create_user('business', User.BUSINESS)
        business_response = self.client.get('/api/profiles/business/')
        customer_response = self.client.get('/api/profiles/customer/')
        self.assertEqual(business_response.status_code, status.HTTP_200_OK)
        self.assertEqual(customer_response.status_code, status.HTTP_200_OK)
        self.assertEqual(business_response.data[0]['user'], business.id)
        self.assertEqual(customer_response.data[0]['user'], customer.id)

    def test_model_string_values(self):
        user = self.create_user('customer', User.CUSTOMER)
        self.assertEqual(str(user), 'customer')
        self.assertEqual(str(user.profile), 'customer')
