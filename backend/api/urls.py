from rest_framework import routers
from django.urls import path, include

from .views import (CustomUserViewSet, TagViewSet,
                    IngredientViewSet, RecipeViewSet, FollowViewSet)

app_name = 'api'

router = routers.DefaultRouter()
# router.register('users/subscriptions', FollowViewSet, basename='subscription')
# router.register('users/(?P<user_id>[^/.]+)/subscriptions', FollowViewSet, basename='subscription')
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('follow', FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
