from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path
from posts import views as posts_views
from django.conf.urls import handler404, handler500

handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa

urlpatterns = [
    # path('404/', include('django.conf.urls')),
    # path('500/', include('django.conf.urls')),
    path("404/", posts_views.page_not_found, name="page_not_found"),
    path("500/", posts_views.server_error, name="server_error"),
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls')),
]
urlpatterns += [
        # path('404/', handler404, name='404'),
        # path('500/', handler500, name='500'),

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
