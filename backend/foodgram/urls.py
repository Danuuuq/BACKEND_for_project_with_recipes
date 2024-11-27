from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from recipes.views import ShortLinkRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:slug>/', ShortLinkRedirectView.as_view(), name='reverse-link')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
