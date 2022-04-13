import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import resolve
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class LoginApiTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('accounts:token_obtain_pair')

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username='test',
            password='pass#123',
            email='test@example.com'
        )
        self.payload = {
            'username': 'test',
            'password': 'pass#123'
        }

    def test_login_url_resolves_to_login_view(self):
        """
        Test that the login url resolves to the login view
        """
        view = resolve(self.url)
        self.assertEqual(view.func.view_class.__name__, 'TokenObtainPairView')

    def test_login_api_success(self):
        """
        Test that the login api returns a token
        """
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIsNotNone(response.data['access'])
        self.assertIsNotNone(response.data['refresh'])

    def test_login_verify_access_login_token(self):
        """
        Test that the access token is valid
        """
        response = self.client.post(self.url, self.payload)
        access_token = response.data['access']
        # verify jwt token
        decoded_dict = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(decoded_dict['user_id'], self.user.id)

    def test_invalid_credentials(self):
        """
        Test that the login api returns a 401 if the credentials are invalid
        """
        self.payload['username'] = 'test'
        self.payload['password'] = 'invalid'
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 401)


