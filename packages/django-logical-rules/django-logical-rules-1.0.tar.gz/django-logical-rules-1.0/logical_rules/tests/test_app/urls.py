from django.conf.urls import patterns, url

import logical_rules
logical_rules.helpers.autodiscover()

from views import ServePizzaView

urlpatterns = patterns(
    '',
    (r'^feed-me/(?P<food>\w+)/$', ServePizzaView.as_view()),
)