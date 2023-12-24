from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Название записки'
    NOTE_TEXT = 'Текст записки'
    NOTE_SLUG = 'test_slug'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='author')
        cls.url = reverse('notes:add')
        cls.after_create_redirect = reverse('notes:success')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
        }

    def test_anon_user_cant_create_note(self):
        response = self.client.post(self.url)
        notes_count = Note.objects.count()
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(notes_count, 0)

    def test_auth_user_can_create_note(self):
        response = self.auth_user.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.after_create_redirect)
        notes_count = Note.objects.count()
        note = Note.objects.get()
        self.assertEqual(notes_count, 1)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_slug_from_title(self):
        response = self.auth_user.post(
            self.url, data={'title': self.NOTE_TITLE, 'text': self.NOTE_TEXT}
        )
        self.assertRedirects(response, self.after_create_redirect)
        notes_count = Note.objects.count()
        note = Note.objects.get()
        self.assertEqual(notes_count, 1)
        self.assertEqual(note.slug, slugify(self.NOTE_TITLE))

    def test_not_unique_slug(self):
        self.auth_user.post(self.url, data=self.form_data)
        response = self.auth_user.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{self.NOTE_SLUG}{WARNING}',
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Название записки'
    NOTE_TEXT = 'Текст записки'
    NEW_NOTE_TITLE = 'Новое название записки'
    NEW_NOTE_TEXT = 'Новый текст записки'
    NOTE_SLUG = 'test_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.after_create_redirect = reverse('notes:success')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.other_user = User.objects.create(username='other_user')
        cls.other_user_client = Client()
        cls.other_user_client.force_login(cls.other_user)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.NOTE_SLUG,))
        cls.delete_url = reverse('notes:delete', args=(cls.NOTE_SLUG,))
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
        }

    def test_author_can_delete_note(self):
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.after_create_redirect)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_non_author_cant_delete_note(self):
        response = self.other_user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.after_create_redirect)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_non_author_cant_edit_note(self):
        response = self.other_user_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
