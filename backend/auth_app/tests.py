import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import Profile, User


def image_file(name='test.png'):
    buffer = BytesIO()
    Image.new('RGB', (1, 1)).save(buffer, format='PNG')
    return SimpleUploadedFile(
        name,
        buffer.getvalue(),
        content_type='image/png',
    )


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

    def registration_data(self, username='newuser', email='new@example.com'):
        return {
            'username': username,
            'email': email,
            'password': 'Testpass123!',
            'repeated_password': 'Testpass123!',
            'type': User.CUSTOMER,
        }

    def test_registration_creates_user_profile_and_token(self):
        response = self.client.post(
            '/api/registration/',
            self.registration_data(),
            format='json',
        )
        user = User.objects.get(username='newuser')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password('Testpass123!'))
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(response.data['email'], 'new@example.com')
        self.assertIn('token', response.data)

    def test_registration_rejects_password_mismatch(self):
        data = self.registration_data()
        data['repeated_password'] = 'Wrongpass123!'
        response = self.client.post('/api/registration/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_rejects_duplicate_email(self):
        self.create_user('existing', User.CUSTOMER)
        data = self.registration_data(email='EXISTING@example.com')
        response = self.client.post('/api/registration/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_token(self):
        user = self.create_user('customer', User.CUSTOMER)
        data = {'username': 'customer', 'password': 'Testpass123!'}
        response = self.client.post('/api/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer')
        self.assertEqual(response.data['email'], user.email)
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
        self.assertEqual(response.data['email'], user.email)
        self.assertIn('created_at', response.data)

    def profile_update_data(self):
        return {
            'first_name': 'Etem',
            'email': 'etem@example.com',
            'location': 'Cologne',
        }

    def assert_profile_values(self, user):
        self.assertEqual(user.first_name, 'Etem')
        self.assertEqual(user.email, 'etem@example.com')
        self.assertEqual(user.profile.location, 'Cologne')

    def test_user_can_update_own_profile(self):
        user = self.create_user('customer', User.CUSTOMER)
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            f'/api/profile/{user.id}/',
            self.profile_update_data(),
            format='json',
        )
        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_profile_values(user)

    def test_profile_rejects_duplicate_email(self):
        user = self.create_user('customer', User.CUSTOMER)
        other = self.create_user('other', User.CUSTOMER)
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            f'/api/profile/{user.id}/',
            {'email': other.email.upper()},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_upload_profile_image(self):
        user = self.create_user('customer', User.CUSTOMER)
        self.client.force_authenticate(user=user)
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.patch(
                    f'/api/profile/{user.id}/',
                    {'file': image_file('profile.png')},
                    format='multipart',
                )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('/media/profile_images/', response.data['file'])

    def test_user_cannot_update_another_profile(self):
        user = self.create_user('customer', User.CUSTOMER)
        other = self.create_user('other', User.CUSTOMER)
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            f'/api/profile/{other.id}/', {'location': 'Berlin'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_lists_require_authentication(self):
        business = self.client.get('/api/profiles/business/')
        customer = self.client.get('/api/profiles/customer/')
        self.assertEqual(business.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(customer.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_lists_use_role_specific_fields(self):
        customer = self.create_user('customer', User.CUSTOMER)
        business = self.create_user('business', User.BUSINESS)
        self.client.force_authenticate(user=customer)
        business_response = self.client.get('/api/profiles/business/')
        customer_response = self.client.get('/api/profiles/customer/')
        business_fields = set(business_response.data[0])
        customer_fields = set(customer_response.data[0])
        self.assertEqual(business_response.data[0]['user'], business.id)
        self.assertEqual(customer_response.data[0]['user'], customer.id)
        self.assertIn('working_hours', business_fields)
        self.assertNotIn('working_hours', customer_fields)
        self.assertNotIn('email', customer_fields)
