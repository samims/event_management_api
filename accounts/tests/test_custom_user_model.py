from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from faker import Faker

from accounts.models import CustomUser


fake = Faker()


class CustomUserModelTest(TransactionTestCase):
    def test_user_is_created_with_valid_email_only(self):
        """
        Test that a user is created with a valid email only and invalid email
        raises an error.
        """
        email = fake.email()
        user = CustomUser.objects.create_user(
            email=email,
            username=fake.text(5),
            password=fake.text(8),
        )
        self.assertEqual(user.email, email)
        self.assertEqual(CustomUser.objects.count(), 1)

        invalid_email = fake.text(10)
        # we can expect a ValidationError here because the email is invalid
        with self.assertRaises(ValidationError):
            CustomUser.objects.create(
                email=invalid_email,
                username=fake.text(5),
                password=fake.text(8)
            )
        # no user created
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_user_is_created_with_only_unique_email(self):
        """
        Test that a user is created with a unique email only and a non-unique
        email raises an error.
        The email field is overridden and there is a validator so this is not
        a django's source code test
        """
        email = fake.email()
        user = CustomUser.objects.create_user(
            email=email,
            username=fake.text(5),
            password=fake.text(8),
        )
        self.assertEqual(user.email, email)
        self.assertEqual(CustomUser.objects.count(), 1)

        # we can expect a ValidationError here because the email is not unique
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email=email,
                username=fake.text(5),
                password=fake.text(8)
            )
        # no user created
        self.assertEqual(CustomUser.objects.count(), 1)




