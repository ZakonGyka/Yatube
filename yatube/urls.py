from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path, re_path

from django.views.static import serve

handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls')),

    re_path(r'^media/(?P<path>.*)$',
            serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$',
            serve, {'document_root': settings.STATIC_ROOT}),
]
urlpatterns += [
        path('about-us/', views.flatpage,
             {'url': '/about-us/'}, name='about'),
        path('terms/', views.flatpage,
             {'url': '/terms/'}, name='terms'),
        path('about/about-author/', views.flatpage,
             {'url': '/about-author/'}, name='author'),
        path('about/about-spec/', views.flatpage,
             {'url': '/about-spec/'}, name='spec'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
