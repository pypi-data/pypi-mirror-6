from django.conf.urls.defaults import url, patterns 

urlpatterns = patterns('django_mce_spellcheck.views',
    url(r'^$', 'spellcheck', name='spellcheck'),
)
