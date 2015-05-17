from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from app import views
from app.views import api

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('vkrsys.app',),
}

urlpatterns = patterns('',
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^social/', include('social_auth.urls')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

    url(r'^api/', include('app.urls_api', namespace='api')),
)

urlpatterns += i18n_patterns('',
    url(r'^', include('app.urls', namespace='app')),
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
                        url('/i18n/', include('django.conf.urls.i18n')),
)

