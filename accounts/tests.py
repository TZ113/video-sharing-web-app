from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase


# Create your tests here.
class CustomUserModelTests(TestCase):

    def setUp(self):
        self.user_model = get_user_model()

        self.user = self.user_model.objects.create_user(
            username="testuser",
            first_name="test",
            last_name="user",
            email="testuser@email.com",
            password="testuserpass123",
        )

    def test_create_user(self):
        user = self.user_model.objects.create_user(
            username="testuser1", email="testuser1@email.com", password="testuser1pass123",
        )
        self.assertEqual(user.username, "testuser1")
        self.assertEqual(user.email, "testuser1@email.com")
        self.assertTrue(user.check_password("testuser1pass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = self.user_model.objects.create_superuser(
            username="admin", email="admin@email.com", password="adminpass123"
        )
        self.assertEqual(admin_user.username, "admin")
        self.assertEqual(admin_user.email, "admin@email.com")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_username_minlength(self):
        with self.assertRaises(ValidationError):
            user = self.user_model(
                username="te", email="testuser1@email.com", password="testuser123"
            )
            user.full_clean()  # This will trigger the validation check

    def test_username_maxlength(self):
        with self.assertRaises(ValidationError):
            user = self.user_model(
                username="testusertestusertestusertestusertestuser",
                email="testuser1@email.com",
                password="testuser123",
            )
            user.full_clean()

    def test_unique_username(self):
        with self.assertRaises(ValidationError):
            user = self.user_model(
                username="testuser",
                email="testuser1@email.com",
                password="testuserpass123",
            )
            user.full_clean()

    def test_email_normalization(self):
        user = self.user_model.objects.create_user(
            username="testuser1",
            email="testuser1@Email.COM",
            password="testuserpass123",
        )
        self.assertEqual(user.email, "testuser1@email.com")

    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            user = self.user_model(
                username="testuser1", email="email", password="testuserpass123"
            )
            user.full_clean()

    def test_unique_email(self):
        with self.assertRaises(ValidationError):
            user = self.user_model(
                username="testuser1",
                email="testuser@email.com",
                password="testuserpass123",
            )
            user.full_clean()

    def test_no_password(self):
        with self.assertRaises(ValidationError):
            user = self.user_model(
                username="testuser1", email="testuser1@email.com", password=None
            )
            user.full_clean()

    def test_password_minlength(self):
        with self.assertRaises(ValidationError):
            self.user_model.objects.create_user(
                username="testuser1", email="testuser1@email.com", password="test"
            )

    def test_full_name(self):
        self.assertEqual(self.user.get_full_name(), "test user")

    def test_full_name_with_empty_firstname(self):
        user = self.user_model.objects.create_user(
            username="testuser1",
            first_name="",
            last_name="user",
            email="testuser1@email.com",
            password="testuserpass123",
        )
        self.assertEqual(user.get_full_name(), "user")

    def test_full_name_with_empty_lastname(self):
        user = self.user_model.objects.create_user(
            username="testuser1",
            first_name="test",
            last_name="",
            email="testuser1@email.com",
            password="testuserpass123",
        )
        self.assertEqual(user.get_full_name(), "test")

    def test_short_name(self):
        self.assertEqual(self.user.get_short_name(), "test")

    def test_string_representation(self):
        self.assertEqual(str(self.user), "testuser with testuser@email.com")
