from django.views.generic import TemplateView
from logical_rules.mixins import RulesMixin

class ServePizzaView(RulesMixin, TemplateView):
    """
        A sample view that tests that the user is asking for a pizza
        
        Permission denied is issued if they're asking for anything else
    """
    template_name = "test_app/serve_pizza.html"
    
    def update_logical_rules(self):

        super(ServePizzaView, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'test_is_pizza',
            'param_callbacks':
            [
                ('word', "get_word")
            ],
        })
        
    def get_word(self):
        """
            The callback for the logical rule
        """
        return self.kwargs['food']