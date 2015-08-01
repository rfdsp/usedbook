from django.conf.urls import patterns, url
from usedbook import views

urlpatterns = patterns('',
    (r'^$', 'usedbook.views.index'),
    (r'^add/$', 'usedbook.views.add'),
    (r'^result/$', 'usedbook.views.result'),
    (r'^(?P<wantedbook_id>\d+)/delete/$', 'usedbook.views.delete'),
)

