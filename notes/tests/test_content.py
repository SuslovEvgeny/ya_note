from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNotesPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор1')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Автор2')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.notes = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            slug='slug',
            author=cls.author
        )

    def test_pages_contains_form(self):
        urls = (
            ('notes:edit', (self.notes.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_author.get(url)
                self.assertIn('form', response.context)

    def test_notes_list_for_author(self):
        url = reverse('notes:list')
        response = self.auth_author.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_notes_list_for_other_author(self):
        url = reverse('notes:list')
        response = self.auth_reader.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)
