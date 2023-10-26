from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
from django.utils import timezone

from notes.models import Note

...
# Дополнительно к News импортируем модель комментария.
from notes.models import Note

User = get_user_model()


class TestNotesPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.notes = Note.objects.create(
            title='Тестовая новость', text='Просто текст.', slug='slug', author=cls.author
        )
        cls.notes_edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.notes_create_url = reverse('notes:add')

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.notes_edit_url)
        self.assertIn('form', response.context)
        response = self.client.get(self.notes_create_url)
        self.assertIn('form', response.context)
    
    def test_obj_list_in_context(self):
        self.client.force_login(self.author)
        response = self.client.get(self.notes_edit_url)
        object_list = response.context['object_list']
        self.assertIn(object_list, settings.NEWS_COUNT_ON_HOME_PAGE) 

    # def test_news_order(self):
    #     response = self.client.get(self.HOME_URL)
    #     object_list = response.context['object_list']
    #     all_dates = [news.date for news in object_list]
    #     sorted_dates = sorted(all_dates, reverse=True)
    #     self.assertEqual(all_dates, sorted_dates)





        

# class TestHomePage(TestCase):
#     HOME_URL = reverse('news:home')

#     @classmethod
#     def setUpTestData(cls):
#         today = datetime.today()
#         all_news = [
#             News(
#                 title=f'Новость {index}',
#                 text='Просто текст.',
#                 date=today - timedelta(days=index)
#             )
#             for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
#         ]
#         News.objects.bulk_create(all_news) 

    # def test_news_count(self):
    #     response = self.client.get(self.HOME_URL)
    #     object_list = response.context['object_list']
    #     news_count = len(object_list)
    #     self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE) 

    # def test_news_order(self):
    #     response = self.client.get(self.HOME_URL)
    #     object_list = response.context['object_list']
    #     all_dates = [news.date for news in object_list]
    #     sorted_dates = sorted(all_dates, reverse=True)
    #     self.assertEqual(all_dates, sorted_dates)


# class TestDetailPage(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.news = News.objects.create(
#             title='Тестовая новость', text='Просто текст.'
#         )
#         cls.detail_url = reverse('news:detail', args=(cls.news.id,))
#         cls.author = User.objects.create(username='Комментатор')
#         now = timezone.now()
#         for index in range(2):
#             comment = Comment.objects.create(
#                 news=cls.news, author=cls.author, text=f'Tекст {index}',
#             )
#             comment.created = now + timedelta(days=index)
#             comment.save()
        
#     def test_comments_order(self):
#         response = self.client.get(self.detail_url)
#         self.assertIn('news', response.context)
#         news = response.context['news']
#         all_comments = news.comment_set.all()
#         self.assertLess(all_comments[0].created, all_comments[1].created)

#     def test_anonymous_client_has_no_form(self):
#         response = self.client.get(self.detail_url)
#         self.assertNotIn('form', response.context)
        
#     def test_authorized_client_has_form(self):
#         self.client.force_login(self.author)
#         response = self.client.get(self.detail_url)
#         self.assertIn('form', response.context)
