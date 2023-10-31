from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()
NOTE_ADD_URL = reverse('notes:add')
NOTE_SUCCESS_URL = reverse('notes:success')


class TestNoteCreate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор1')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        """Зарегистрированный пользователь может создавать заметку."""
        response = self.auth_author.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTE_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1,
                         'Убедитесь, что пользователь может создать заметку.')
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'],
                         'Убедитесь, что в заметку передаётся тот заголовок.')
        self.assertEqual(new_note.text, self.form_data['text'],
                         'Убедитесь, что в заметку передаётся тот текст.')
        self.assertEqual(new_note.slug, self.form_data['slug'],
                         'Убедитесь, что в заметку передаётся тот slug.')
        self.assertEqual(new_note.author, self.author,
                         'Убедитесь, что в заметку передаётся тот автор.')

    def test_anonymous_user_cant_create_note(self):
        """Не зарегистрированный пользователь может создавать заметку."""
        response = self.client.post(NOTE_ADD_URL, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={NOTE_ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0,
                         'Убедитесь, что не зарегистрированный пользователь'
                         ' не может создать заметку.')

    def test_empty_slug(self):
        """Автодобавление slug к заметке."""
        self.form_data.pop('slug')
        response = self.auth_author.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTE_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug,
                         'Убедитесь, что slug автоматические добавляется'
                         ' к заметке.')


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор1')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.notes = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            slug='slug',
            author=cls.author
        )

    def test_not_unique_slug(self):
        """Уникальность slug."""
        self.form_data['slug'] = self.notes.slug
        response = self.auth_author.post(NOTE_ADD_URL, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.notes.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1,
                         'Убедитесь, что slug не может быть не уникальным')

    def test_author_can_edit_note(self):
        """Автор может править свою заметку."""
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.auth_author.post(url, self.form_data)
        self.assertRedirects(response, NOTE_SUCCESS_URL,
                             'Убедитесь, что автор может править свою заметку')
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.form_data['title'])
        self.assertEqual(self.notes.text, self.form_data['text'])
        self.assertEqual(self.notes.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Другой пользователь не может править заметку автора."""
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.auth_reader.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         'Убедитесь, что другой пользователь'
                         ' не может править заметку автора.')
        note_from_db = Note.objects.get(id=self.notes.id)
        self.assertEqual(self.notes.title, note_from_db.title)
        self.assertEqual(self.notes.text, note_from_db.text)
        self.assertEqual(self.notes.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        url = reverse('notes:delete', args=(self.notes.slug,))
        response = self.auth_author.post(url)
        self.assertRedirects(response, NOTE_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 0,
                         'Убедитесь, что автор может удалять свою заметку.')

    def test_other_user_cant_delete_note(self):
        """Другой пользователь не может удалить заметку автора."""
        url = reverse('notes:delete', args=(self.notes.slug,))
        response = self.auth_reader.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1,
                         'Убедитесь, что другой пользователь'
                         ' не может удалить заметку автора.')
