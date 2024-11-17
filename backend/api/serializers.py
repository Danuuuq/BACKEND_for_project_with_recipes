import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, validators

from users.models import User
from core.models import Tag, Follow
from recipes.models import Ingredient, Recipe


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


class FollowFields(serializers.RelatedField):

    def to_representation(self, value):
        cur_user = self.context['request'].user
        if cur_user.is_anonymous:
            return False
        return value.filter(user=cur_user).exists()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = FollowFields(read_only=True, source='following')
    # is_subscribed = FollowFields(read_only=True, source='following')
    # ПОПРОБОВАТЬ ТАК РЕАЛИЗОВАТЬ!
    # def get_is_subscribed(self, obj):
    #     cur_user = self.context['request'].user
    #     if cur_user.is_anonymous:
    #         return False
    #     return obj.filter(user=cur_user).exists()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'is_subscribed',
                  'last_name', 'email', 'avatar')
        read_only = ('id', 'avatar')


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'password', 'username',
                  'first_name', 'last_name')
        read_only = ('id', )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        lookup_field = 'slug'
        read_only = ('id',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = FollowFields(read_only=True, source='save')
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
    is_in_shopping_cart = FollowFields(read_only=True, source='purchase')
    image = Base64ImageField(required=True, allow_null=False)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only = ('id', 'is_favorited', 'is_in_shopping_cart')


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        required=True
    )

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        return data

    class Meta:
        model = Follow
        fields = ('user', 'following')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на пользователя'
            )
        ]
    
