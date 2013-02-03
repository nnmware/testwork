from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from django.contrib import admin
from testwork.views import manage_json
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^manage/$', manage_json, name='manage'),
    url(r'^manage/json/(?P<model_name>\w+)/$', manage_json, name='manage_json'),
    url(r'^admin/', include(admin.site.urls)),
)
