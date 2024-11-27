from rest_framework import permissions, viewsets, views, status
from django.db.models import Exists, OuterRef, BooleanField, Prefetch, Value
from django.http import FileResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    ShoppingCartSerializer, FavoriteSerializer)
from core.models import Tag
from .models import Ingredient, Recipe, User
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
    queryset = Recipe.objects.prefetch_related('recipetag',
                                               'recipeingredient').all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        if self.request.user.is_anonymous:
            queryset = self.queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )
            return queryset
        favorite = self.request.user.saver.filter(recipe=OuterRef('pk'))
        shopping_cart = self.request.user.buyer.filter(purchase=OuterRef('pk'))
        queryset = self.queryset.annotate(is_favorited=Exists(favorite),
                                          is_in_shopping_cart=Exists(
                                              shopping_cart))
        queryset = queryset.prefetch_related(Prefetch(
            'author', queryset=User.objects.is_subscribe(self.request.user)))
        return queryset

    def get_permissions(self):
        if self.action in ['delete_shopping_cart', 'delete_favorite']:
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
    
    @action(methods=['post'], detail=True, url_path='shopping_cart')
    def add_shopping_cart(self, request, *args, **kwargs):
        data_following = {'purchase': self.kwargs['pk']}
        serializer = ShoppingCartSerializer(data=data_following,
                                            context={'request': request})
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @add_shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        purchases = get_object_or_404(self.get_object().purchase.all(),
                                      user=user)
        self.perform_destroy(purchases)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post'], detail=True, url_path='favorite')
    def add_favorite(self, request, *args, **kwargs):
        data_following = {'recipe': self.kwargs['pk']}
        serializer = FavoriteSerializer(data=data_following,
                                        context={'request': request})
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @add_favorite.mapping.delete
    def delete_favorite(self, request, *args, **kwargs):
        user = self.request.user
        favorite = get_object_or_404(self.get_object().favorite.all(),
                                     user=user)
        self.perform_destroy(favorite)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        return create_shopping_cart(self.request.user)


class ShortLinkRedirectView(views.APIView):
    lookup_field = 'short_url'
    permission_classes = (permissions.AllowAny,)

    def get(self, request, slug):
        recipe = get_object_or_404(Recipe, short_url=slug)
        return redirect('api:recipe-detail', recipe.id)
