from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestHomePage(TestCase):
    HOME_URL = reverse('notes:home')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(username='user')

    def test_auth_client_has_add_button(self):
        self.client.force_login(self.user)
        response = self.client.get(self.HOME_URL)
        self.assertIn('href="/add/"', str(response.content))

    def test_anon_client_has_no_add_button(self):
        response = self.client.get(self.HOME_URL)
        self.assertNotIn('href="/add/"', str(response.content))
