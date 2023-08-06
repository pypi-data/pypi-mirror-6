#encoding: utf-8

from django.test import TestCase, Client
# from urlbreadcrumbs.tests.views import index


class BreadcrumbsTest(TestCase):

    def setUp(self):
        if not hasattr(self, 'client'):
            self.client = Client()

    def test_index(self):
        res = self.client.get('/')
        assert res.status_code == 200

        text = "A title for a home page"
        self.assertContains(res, text, count = 3, html=False)

    def test_sub1(self):
        res = self.client.get('/test1/')
        assert res.status_code == 200

        text = "Index page of Test1"
        self.assertContains(res, text, count = 3, html=False)

    def test_url(self):
        res = self.client.get('/test1/aaa/')
        assert res.status_code == 200

        text = "Test1 subpage via custom url function"
        self.assertContains(res, text, count = 3, html=False)
