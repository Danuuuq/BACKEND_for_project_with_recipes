from django.db.models import BooleanField, Prefetch, Value, Count
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, viewsets, views, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.settings import api_settings

from . import constants
from .filters import RecipeFilter, IngredientFilter
from .permissions import OwnerOrReadOnly
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    ShoppingCartSerializer, FavoriteSerializer, AvatarSerializer,
    FollowSerializer, UserFollowSerializer)
from .utils import create_shopping_cart
from recipes.models import Ingredient, Recipe, User, Tag


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
    filterset_class = IngredientFilter
    http_method_names = ['get']


class RecipeViewSet(viewsets.ModelViewSet):
    model = Recipe
    queryset = Recipe.tags_and_ingredients
    serializer_class = RecipeSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_pagination_class(self):
        if self.request.query_params.get('limit') is None:
            return api_settings.DEFAULT_PAGINATION_CLASS
        return self.pagination_class

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
        if self.action not in constants.SAFE_ACTION_FOR_RECIPE:
            return (OwnerOrReadOnly(),)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_short_link(self, request, *args, **kwargs):
        short_link = self.get_object().short_url
        data = {'short-link': reverse('redirect-link', args=[short_link],
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
            ShoppingCartSerializer, 'purchases',
            'purchase', request, *args, **kwargs
        )

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        return self.create_or_delete_for_action(
            FavoriteSerializer, 'favorites',
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
        return redirect(f'/recipes/{recipe.id}/')


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.with_related_data()
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_anonymous:
            return queryset.annotate(
                is_subscribed=Value(False, output_field=BooleanField()))
        return queryset.is_subscribe(self.request.user).annotate(
            recipes_count=Count('recipes'))

    def get_permissions(self):
        if self.action in constants.ACTION_FOR_USER:
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def update_avatar(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(is_subscribed=True)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = UserFollowSerializer(page, many=True,
                                              context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = UserFollowSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, url_path='subscribe')
    def create_subscribe(self, request, *args, **kwargs):
        following = self.get_object()
        data = {'following': following.id}
        serializer = FollowSerializer(data=data,
                                      context={'request': request})
        if serializer.is_valid():
            serializer.save(user=self.request.user, following=following)
            user_data = UserFollowSerializer(self.get_object(),
                                             context={'request': request}).data
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @create_subscribe.mapping.delete
    def delete_subscribe(self, request, *args, **kwargs):
        user = self.request.user
        follow = get_object_or_404(self.get_object().followings.all(),
                                   user=user)
        self.perform_destroy(follow)
        return Response(status=status.HTTP_204_NO_CONTENT)
