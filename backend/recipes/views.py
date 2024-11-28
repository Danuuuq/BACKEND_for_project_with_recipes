from rest_framework import permissions, viewsets, views, status
from django.db.models import BooleanField, Prefetch, Value
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    ShoppingCartSerializer, FavoriteSerializer)
from .models import Ingredient, Recipe, User, Tag
from .filters import RecipeFilter
from .permissions import OwnerOrReadOnly
from .utils import create_shopping_cart


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
    queryset = Recipe.tags_and_ingredients
    serializer_class = RecipeSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )
        return (queryset.all().is_favorite_and_shop_cart(user)
                .prefetch_related(Prefetch(
                    'author', queryset=User.objects.is_subscribe(
                        self.request.user))))

    def get_permissions(self):
        if self.action in ['shopping_cart', 'favorite']:
            return (permissions.IsAuthenticated(),)
        if self.action not in settings.SAFE_ACTION_FOR_RECIPE:
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

    def create_or_delete_for_action(self, serializer_class, related_name,
                                    instance_name, request, *args, **kwargs):
        user = self.request.user
        data = {instance_name: self.kwargs['pk']}

        if request.method == 'POST':
            serializer = serializer_class(data=data,
                                          context={'request': request})
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            instance = get_object_or_404(
                getattr(self.get_object(), related_name).all(), user=user)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        return self.create_or_delete_for_action(
            ShoppingCartSerializer, 'purchase',
            'purchase', request, *args, **kwargs
        )

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        return self.create_or_delete_for_action(
            FavoriteSerializer, 'favorite',
            'recipe', request, *args, **kwargs
        )

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        return create_shopping_cart(self.request.user)


class ShortLinkRedirectView(views.APIView):
    lookup_field = 'short_url'
    permission_classes = (permissions.AllowAny,)

    def get(self, request, slug):
        recipe = get_object_or_404(Recipe, short_url=slug)
        return redirect('api:recipe-detail', recipe.id)
