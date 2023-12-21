import pytest

from notes.models import Note


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def note(author):
    note = Note.objects.create(
        title='Title',
        text='Note text',
        slug='note-slug',
        author=author,
    )
    return note


@pytest.fixture
def slug_for_args(note):
    return (note.slug,)
