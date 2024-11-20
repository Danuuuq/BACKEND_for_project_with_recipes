import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from core.models import Tag
from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag


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
    id = serializers.SlugRelatedField(read_only=True, slug_field='id', source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeTagSerializer(serializers.Serializer):
    # id = serializers.SlugRelatedField(queryset=Tag.objects.all(),
    #                                   slug_field='id', source='tag')
    id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

    def to_internal_value(self, data):
        try:
            data = Tag.objects.get(id=data)
        except Tag.DoesNotExist:
            raise serializers.ValidationError(
                {'tag': f'Тег с id: {data} отсутствует.'})
        return data

    class Meta:
        model = RecipeTag
        fields = ('recipe', 'tag')
        read_only = ('recipe', )


class RecipeSerializer(serializers.ModelSerializer):
    # is_favorited = BooleanAddField(read_only=True, source='save')
    tags = RecipeTagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    # is_in_shopping_cart = BooleanAddField(read_only=True, source='purchase')
    image = Base64ImageField(required=True, allow_null=False)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        breakpoint()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient_data in ingredients:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=amount)
        return recipe

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only = ('id', 'is_favorited', 'is_in_shopping_cart')