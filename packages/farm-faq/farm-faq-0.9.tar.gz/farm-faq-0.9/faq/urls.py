from django.conf.urls import patterns, url

urlpatterns = patterns('faq.views',
   url(r'^$', 'index', name='faq-index'),
)
