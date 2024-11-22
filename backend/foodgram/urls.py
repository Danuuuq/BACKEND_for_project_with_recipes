from django.contrib import admin
from django.urls import path, include

from recipes.views import ShortLinkRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:slug>/', ShortLinkRedirectView.as_view(), name='reverse-link')
]
