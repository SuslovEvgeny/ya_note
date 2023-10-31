from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Гость')
        cls.notes = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            text='Текст поста'
        )

    def test_no_loginrequired_pages_availability(self):
        """Доступность страниц для пользователей без регистрации."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Убедитесь, что на страницу {url}'
                                 ' есть доступ пользователю без регистрации.')

    def test_loginrequired_pages_availability(self):
        """Доступность страниц для разных пользователей."""
        urls = (
            ('notes:detail', (self.notes.slug,)),
            ('notes:edit', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status,
                                     f'Убедитесь, что на страницу {url}'
                                     ' есть доступ нужному пользователю.')

    def test_only_logined_pages_availability(self):
        """Доступность страниц для зарегитрированных пользователей."""
        urls = (
            'notes:add',
            'notes:success',
            'notes:list',
        )
        self.client.force_login(self.author)
        for name in urls:
            with self.subTest(user=self.author, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Убедитесь, что на страницу {url} есть'
                                 ' доступ зарегистрированному пользователю.')

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректов для пользователей без регистрации."""
        urls = (
            ('notes:detail', (self.notes.slug,)),
            ('notes:edit', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url,
                                     'Убедитесь, что пользователь без'
                                     ' регистрации при переходе на страницу'
                                     f' {url} перенаправлятся на логин.')
