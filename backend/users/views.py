from djoser import views
from django.conf import settings
from django.db.models import Count, Value, BooleanField
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import (AvatarSerializer, FollowSerializer,
                               UserFollowSerializer)
from .models import User


class CustomUserViewSet(views.UserViewSet):
    queryset = User.objects.with_related_data()

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_anonymous:
            return queryset.annotate(
                is_subscribed=Value(False, output_field=BooleanField()))
        return queryset.is_subscribe(self.request.user).annotate(
            recipes_count=Count('recipes'))

    def get_permissions(self):
        if self.action in settings.ACTION_FOR_USER:
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create_subscribe', 'delete_subscribe']:
            return FollowSerializer
        return super().get_serializer_class()

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
        follow = get_object_or_404(self.get_object().following.all(),
                                   user=user)
        self.perform_destroy(follow)
        return Response(status=status.HTTP_204_NO_CONTENT)
