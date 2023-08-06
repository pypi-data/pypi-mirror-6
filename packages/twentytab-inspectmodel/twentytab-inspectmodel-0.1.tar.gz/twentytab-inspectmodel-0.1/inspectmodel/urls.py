from . import conf
from django.conf.urls import *


urlpatterns = patterns('',
    (r'^admin/inspect/browse/$', 'inspectmodel.views.browse'),
)
