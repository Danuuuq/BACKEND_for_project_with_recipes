from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser import views
from django.conf import settings
from django.shortcuts import get_object_or_404

from users.serializers import AvatarSerializer, FollowSerializer
from recipes.models import User


class CustomUserViewSet(views.UserViewSet):
    queryset = User.objects.prefetch_related('follower').all()

    def get_permissions(self):
        if (self.action in settings.ACTION_FOR_USER
            and self.request.user.is_anonymous):
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(methods=['put'], detail=False, url_path='me/avatar')
    def update_avatar(self, request, *args, **kwargs):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @update_avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, url_path='subscribe',
            serializer_class=FollowSerializer)
    def create_subscribe(self, request, *args, **kwargs):
        data_following = {'following': self.kwargs['id']}
        serializer = FollowSerializer(data=data_following,
                                      context={'request': request})
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @create_subscribe.mapping.delete
    def delete_subscribe(self, request, *args, **kwargs):
        user = self.request.user
        follow = get_object_or_404(self.get_object().following.all(),
                                   user=user)
        self.perform_destroy(follow)
        return Response(status=status.HTTP_204_NO_CONTENT)