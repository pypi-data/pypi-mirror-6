"""
    Test that rules are detected in rules.py and added
    to the registry correctly
"""

from django.test import TestCase
from django.test.client import Client

class MixinTest(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass
            
    def test_rules(self):
        response = self.client.get('/feed-me/hamburger/')
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get('/feed-me/pizza/')
        self.assertEqual(response.status_code, 200)
