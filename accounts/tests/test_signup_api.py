from django.contrib.auth import get_user_model
from django.urls import resolve
from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


fake = Faker()


class SignupApiTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('accounts:signup')

    def setUp(self) -> None:
        self.payload = {
            'email': fake.email(),
            'username': fake.user_name(),
            'password': fake.password(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
        }

    def test_url_resolves_to_signup_view(self):
        """
        Test that the signup url resolves to the signup view
        """
        view = resolve(self.url)
        self.assertEqual(view.func.view_class.__name__, 'SignUpAPIView')

    def test_signup_api_returns_201_status_code_on_success(self):
        """
        Test that the signup api returns a 201 status code on success
        """
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_signup_api_creates_user(self):
        """
        Test that the signup api creates a user
        """
        self.client.post(self.url, self.payload)
        # db count should be 1
        self.assertEqual(get_user_model().objects.count(), 1)

        # makes sure the user is created with proper data
        self.assertEqual(
            get_user_model().objects.get(username=self.payload['username']).username,
            self.payload['username']
        )

    def test_signup_api_returns_user_data_on_success(self):
        """
        Test that the signup api returns user data on success
        """
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.data['username'], self.payload['username'])
        self.assertEqual(response.data['email'], self.payload['email'])
        self.assertEqual(response.data['first_name'], self.payload['first_name'])
        self.assertEqual(response.data['last_name'], self.payload['last_name'])

    def test_response_should_not_contain_password(self):
        """
        Test that the response does not contain the password
        """
        response = self.client.post(self.url, self.payload)
        self.assertNotIn('password', response.data)

    def test_signup_hashes_user_password_successfully(self):
        """
        Test that the signup api hashes the user password successfully
        """
        self.client.post(self.url, self.payload)

        # makes sure the user is created with proper data
        self.assertNotEqual(
            get_user_model().objects.get(username=self.payload['username']).password,
            self.payload['password']
        )

    def test_signup_api_returns_400_status_code_on_failure(self):
        """
        Test that the signup api returns a 400 status code on failure
        """
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_api_returns_error_message_on_failure(self):
        """
        Test that the signup api returns an error message on failure
        """
        response = self.client.post(self.url, {})
        self.assertEqual(response.data['email'][0], 'This field is required.')
        self.assertEqual(response.data['username'][0], 'This field is required.')
        self.assertEqual(response.data['password'][0], 'This field is required.')

    def test_signup_api_returns_400_status_code_on_invalid_email(self):
        """
        Test that the signup api returns a 400 status code on invalid email
        """
        self.payload['email'] = 'invalid_email'
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
