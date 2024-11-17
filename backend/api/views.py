from rest_framework.views import APIView
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from djoser.conf import settings

from .serializers import (AvatarSerializer, TagSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer)
from core.models import Tag
from recipes.models import Ingredient, Recipe, User


class CustomUserViewSet(views.UserViewSet):

    def get_permissions(self):
        if (self.action in ['me', 'avatar', 'subscriptions']
            and self.request.user.is_anonymous):
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    def update_avatar(self, request, *args, **kwargs):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete_avatar(self, request, *args, **kwargs):
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def avatar(self, request, *args, **kwargs):
        if self.request.method == 'PUT':
            return self.update_avatar(request, *args, **kwargs)
        elif self.request.method == 'DELETE':
            return self.delete_avatar(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_path='subscriptions')
    def subscribe(self, request, *args, **kwargs):
        pass


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
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.AllowAny,)
    # pagination_class = None
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('name',)
    # http_method_names = ['get']
    
    def perform_create(self, serializer):
        # breakpoint()
        serializer.save(author=self.request.user)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('following__username', )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return User.objects.get(username=user).follower.all()
