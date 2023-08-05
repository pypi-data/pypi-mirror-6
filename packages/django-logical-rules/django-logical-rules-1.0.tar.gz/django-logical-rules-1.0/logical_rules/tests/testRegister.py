"""
    Test that rules are detected in rules.py and added
    to the registry correctly
"""

from django.test import TestCase

import logical_rules

class RulesTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
            
    def test_rules(self):
        self.assertTrue(logical_rules.site.is_registered('test_is_pizza'))
        self.assertTrue(logical_rules.site.test_rule('test_is_pizza', "pizza"))
        self.assertFalse(logical_rules.site.test_rule('test_is_pizza', "hamburger"))
