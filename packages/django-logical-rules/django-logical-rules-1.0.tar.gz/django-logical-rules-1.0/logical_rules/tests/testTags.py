from django.test import TestCase
from django.template import Template, Context

class TemplateTagTest(TestCase):

    def setUp(self):
        pass

    def test_tag(self):
        content = (
                    "{% load logical_rules_tags %}"
                    "This is a {% testrule test_is_pizza 'pizza' %}test{% endtestrule %}"
                    "{% testrule test_is_pizza 'calzone' %}So is this...{% endtestrule %}"
                )
        expected = "This is a test"
        r = Template(content).render(Context({}))
        self.assertEqual(expected, r)

