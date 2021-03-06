from django.test import TestCase
from django.test.client import Client

class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_register_page(self):
        data = {
            'username' : 'test_user',
            'email' : 'test_user@henry.com',
            'password1': 'pass123',
            'password2': 'pass123'
        }
        response = self.client.post('/register/',data)
        self.assertEqual(response.status_code, 302)
