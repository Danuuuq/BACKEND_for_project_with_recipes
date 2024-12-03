import base64

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers, validators

from .models import (Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, PurchaseUser, Favorite, Tag)
from users.serializers import UserSerializer, RecipeFollowSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        lookup_field = 'slug'
        read_only = ('id', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only = ('id',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient', required=True)
    name = serializers.SlugRelatedField(source='ingredient', slug_field='name',
                                        read_only=True)
    measurement_unit = (serializers
                        .SlugRelatedField(source='ingredient',
                                          slug_field='measurement_unit',
                                          read_only=True))

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeTagSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        instance = instance.tag
        return super().to_representation(instance)

    def to_internal_value(self, data):
        try:
            data = Tag.objects.get(id=data)
        except Tag.DoesNotExist:
            raise serializers.ValidationError(
                {'tag': f'Тег с id: {data} отсутствует.'})
        return data

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        lookup_field = 'slug'
        read_only = ('id', 'name', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    tags = RecipeTagSerializer(many=True, source='recipetag', required=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredient',
                                             required=True)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False)
    image = Base64ImageField(required=True, allow_null=False)
    author = UserSerializer(
        read_only=True, default=serializers.CurrentUserDefault())

    def _validate_non_empty_field(self, attrs, field, error_field):
        if field not in attrs or len(attrs.get(field)) == 0:
            raise serializers.ValidationError(
                {error_field: 'Обязательное поле.'})

    def validate(self, attrs):
        self._validate_non_empty_field(attrs,
                                       'recipetag', 'tags')
        self._validate_non_empty_field(attrs,
                                       'recipeingredient', 'ingredients')
        return super().validate(attrs)

    def _validate_unique_items(self, attrs, field, error_field):
        if field == 'ingredient':
            items = [item['ingredient'] for item in attrs]
        else:
            items = attrs
        if len(items) != len(set(items)):
            raise serializers.ValidationError(error_field)

    def validate_ingredients(self, attrs):
        self._validate_unique_items(attrs, 'ingredient',
                                    'Присутствуют повторяющиеся ингредиенты')
        return super().validate(attrs)

    def validate_tags(self, attrs):
        self._validate_unique_items(attrs, 'tag',
                                    'Присутствуют повторяющиеся теги')
        return super().validate(attrs)

    @staticmethod
    def _related_data_save(instance, tags, ingredients):
        RecipeTag.objects.bulk_create(
            [RecipeTag(recipe=instance, tag=tag) for tag in tags])
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'])
            for ingredient in ingredients
        ])

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('recipetag')
        ingredients = validated_data.pop('recipeingredient')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.recipeingredient.all().delete()
        instance.recipetag.all().delete()
        self._related_data_save(instance, tags, ingredients)
        return instance

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('recipetag')
        ingredients = validated_data.pop('recipeingredient')
        recipe = Recipe.objects.create(**validated_data)
        self._related_data_save(recipe, tags, ingredients)
        return recipe

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only = ('id', 'author')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author')
            ),
        ]


class BaseActionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True,
        default=serializers.CurrentUserDefault())
    purchase = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='id',
        required=True
    )

    class Meta:
        abstract = True


class ShoppingCartSerializer(BaseActionSerializer):

    def to_representation(self, instance):
        recipe_data = RecipeFollowSerializer(instance.purchase,
                                             context=self.context).data
        return recipe_data

    class Meta:
        model = PurchaseUser
        fields = ('user', 'purchase')
        read_only = ('user',)

        validators = [
            validators.UniqueTogetherValidator(
                queryset=PurchaseUser.objects.all(),
                fields=('user', 'purchase'),
                message='Рецепт уже добавлен в покупки.'
            )
        ]


class FavoriteSerializer(BaseActionSerializer):

    def to_representation(self, instance):
        recipe_data = RecipeFollowSerializer(instance.recipe,
                                             context=self.context).data
        return recipe_data

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only = ('user',)

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное.'
            )
        ]
