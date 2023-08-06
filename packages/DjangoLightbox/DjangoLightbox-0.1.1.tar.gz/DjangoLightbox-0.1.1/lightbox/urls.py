from django.conf.urls import patterns, url
from lightbox.views import ImagePageView

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/(?P<path>.*)/$', 
    ImagePageView.as_view(), name="lightbox"),
)