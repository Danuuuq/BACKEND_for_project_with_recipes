from rest_framework import routers
from django.urls import path, include

from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet
from users.views import CustomUserViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
