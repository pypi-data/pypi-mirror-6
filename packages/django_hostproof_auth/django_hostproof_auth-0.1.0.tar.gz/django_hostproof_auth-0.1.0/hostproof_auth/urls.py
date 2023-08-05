from django.conf.urls import patterns, url

from hostproof_auth import views

urlpatterns = patterns('hostproof_auth.views',
    url('^register/$', view='register', name='hostproof_auth_register'),
    url('^challenge/$', view='challenge', name='hostproof_auth_challenge'),
)
