from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^photologue/', include('photologue.urls')),
)
