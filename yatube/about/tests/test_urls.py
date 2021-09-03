from http import HTTPStatus

from django.test import Client, TestCase


class URLsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage_response_status_code(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_page_response_status_code(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_correct_templates_usage(self):
        urls_and_corresponding_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in urls_and_corresponding_templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
