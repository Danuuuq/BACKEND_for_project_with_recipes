import django_filters

from .models import Recipe, Tag, Ingredient


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tag__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        conjoined=False
    )
    is_in_shopping_cart = django_filters.CharFilter(
        method='method_for_shopping_cart')
    is_favorited = django_filters.CharFilter(method='method_for_favorited')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')

    def method_for_favorited(self, queryset, name, value):
        value = True if value == '1' else False
        return queryset.filter(is_favorited=value)

    def method_for_shopping_cart(self, queryset, name, value):
        value = True if value == '1' else False
        return queryset.filter(is_in_shopping_cart=value)


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
