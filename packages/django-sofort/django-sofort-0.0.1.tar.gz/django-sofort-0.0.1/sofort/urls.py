from django.conf.urls import patterns, url

urlpatterns = patterns('sofort.views', url(r'^$', 'notification', name="sofort-notification"))