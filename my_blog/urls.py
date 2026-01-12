from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from posts.views import PostList

urlpatterns = [
    path('', PostList.as_view(), name='home'),  # Главная
    path('admin/', admin.site.urls),
    # path('users/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('posts/', include('posts.urls')),
    path('chat/', include('chat.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)