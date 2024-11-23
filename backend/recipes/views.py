from rest_framework import permissions, viewsets, views
from django.shortcuts import get_object_or_404, redirect
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer
from core.models import Tag
from .models import Ingredient, Recipe
from .filters import RecipeFilter
from .permissions import OwnerOrReadOnly


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    http_method_names = ['get']


class RecipeViewSet(viewsets.ModelViewSet):
    model = Recipe
    queryset = Recipe.objects.prefetch_related('recipetag',
                                               'recipeingredient').all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action not in ['list', 'retrieve', 'get_short_link']:
            return (OwnerOrReadOnly(),)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_short_link(self, request, *args, **kwargs):
        short_link = self.get_object().short_url
        data = {'short-url': reverse('reverse-link', args=[short_link],
                                     request=request)}
        return Response(data)


class ShortLinkRedirectView(views.APIView):
    lookup_field = 'short_url'
    permission_classes = (permissions.AllowAny,)

    def get(self, request, slug):
        recipe = get_object_or_404(Recipe, short_url=slug)
        return redirect('api:recipe-detail', recipe.id)
