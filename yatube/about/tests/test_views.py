from django.test import Client, TestCase
from django.urls import reverse


class ViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_views_correct_templates_usage(self):
        """View-функция использует соответствующий шаблон."""
        views_names_and_corresponding_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

        for (reverse_name,
             template) in views_names_and_corresponding_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
