import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, validators

from users.models import User, Follow
from recipes.models import Recipe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True,
                                             default=False)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')
        read_only = ('id', 'avatar')


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'password', 'username',
                  'first_name', 'last_name')
        read_only = ('id', )


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserFollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    def get_recipes(self, obj):
        rec_limit = self.context['request'].query_params.get('recipes_limit')
        limit = None if rec_limit is None else int(rec_limit)
        return RecipeFollowSerializer(
            obj.recipes.all()[:limit], many=True).data

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')
        read_only = ('id', 'avatar')


class FollowSerializer(UserSerializer):
    user = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True,
        default=serializers.CurrentUserDefault())

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        return data

    class Meta:
        model = Follow
        fields = ('user', 'following')
        read_only = ('user', 'following')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на пользователя'
            )
        ]
