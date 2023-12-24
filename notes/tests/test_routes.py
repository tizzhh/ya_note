from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')

        cls.note = Note.objects.create(
            title='title', text='text', slug='title', author=cls.author
        )

    def test_pages_availability_for_anon_user(self):
        names = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        )

        for name in names:
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        names = (
            'notes:list',
            'notes:success',
            'notes:add'
        )
        self.client.force_login(self.author)
        for name in names:
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_view_edit_delete(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        names = (
            'notes:edit',
            'notes:detail',
            'notes:delete',
        )

        for user, status in user_statuses:
            self.client.force_login(user)

            for name in names:
                with self.subTest(user=user, name=name, args=self.note.slug):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_user(self):
        names = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )

        login_url = reverse('users:login')

        for name, args in names:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
