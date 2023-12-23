from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):
    HOME_URL = reverse('notes:home')

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='reader')
        cls.author = User.objects.create(username='author')

        cls.note = Note.objects.create(
            title='title', text='text', slug='title', author=cls.author
        )

    def test_auth_client_has_add_button(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.HOME_URL)
        self.assertIn('href="/add/"', str(response.content))

    def test_anon_client_has_no_add_button(self):
        response = self.client.get(self.HOME_URL)
        self.assertNotIn('href="/add/"', str(response.content))

    def test_notes_list_for_different_users(self):
        names = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in names:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertEqual(self.note in object_list, note_in_list)

    def test_pages_contains_form(self):
        names = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in names:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
