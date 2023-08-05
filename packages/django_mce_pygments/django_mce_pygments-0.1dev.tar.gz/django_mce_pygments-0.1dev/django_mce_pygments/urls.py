from django.conf.urls.defaults import url, patterns 

urlpatterns = patterns('django_mce_pygments.views',
    url(r'^renderer/$', 'pygments', name='pygments'),
)
