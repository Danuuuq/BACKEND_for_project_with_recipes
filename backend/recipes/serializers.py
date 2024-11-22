import base64

from django.core.files.base import ContentFile
from django.db import IntegrityError
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueTogetherValidator

from core.models import Tag
from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag
from users.serializers import UserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class BooleanAddField(serializers.RelatedField):

    def to_representation(self, value):
        cur_user = self.context['request'].user
        if cur_user.is_anonymous:
            return False
        return value.filter(user=cur_user).exists()


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
    is_favorited = BooleanAddField(read_only=True, source='favorite')
    tags = RecipeTagSerializer(many=True, source='recipetag', required=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredient',
                                             required=True)
    is_in_shopping_cart = BooleanAddField(read_only=True, source='purchase')
    image = Base64ImageField(required=True, allow_null=False)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault())

    def validate_ingredients(self, attrs):
        if len(attrs) == 0:
            raise serializers.ValidationError('Обязательное поле.')
        return super().validate(attrs)

    def validate_tags(self, attrs):
        if len(attrs) == 0:
            raise serializers.ValidationError('Обязательное поле.')
        return super().validate(attrs)

    def update(self, instance, validated_data):
        tags = validated_data.pop('recipetag')
        ingredients = validated_data.pop('recipeingredient')
        Recipe.objects.update(**validated_data)
        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for tag in tags:
            RecipeTag.objects.create(recipe=instance, tag=tag)
        for ingredient_data in ingredients:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=instance,
                                            ingredient=ingredient,
                                            amount=amount)
        return instance

    def create(self, validated_data):
        tags = validated_data.pop('recipetag')
        ingredients = validated_data.pop('recipeingredient')
        try:
            recipe = Recipe.objects.create(**validated_data)
            for tag in tags:
                RecipeTag.objects.create(recipe=recipe, tag=tag)
            for ingredient_data in ingredients:
                ingredient = ingredient_data['ingredient']
                amount = ingredient_data['amount']
                RecipeIngredient.objects.create(recipe=recipe,
                                                ingredient=ingredient,
                                                amount=amount)
        except IntegrityError:
            raise exceptions.ValidationError(
                'Комбинации рецепт-ингредиент или рецепт-тег не уникальны.')
        return recipe

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only = ('id', )

        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author')
            ),
        ]
