from django.db import models


class IngredientQuerySet(models.QuerySet):

    def with_related_data(self):
        return self.prefetch_related('ingredient', )


class IngredientManager(models.Manager):

    def get_queryset(self):
        return IngredientQuerySet(self.model).with_related_data()


class RecipeQuerySet(models.QuerySet):

    def with_related_data(self):
        return self.prefetch_related('recipetag', 'recipeingredient')

    def is_favorite_and_shop_cart(self, user):
        favorite = user.saver.filter(recipe=models.OuterRef('pk'))
        shopping_cart = user.buyer.filter(purchase=models.OuterRef('pk'))
        return self.annotate(is_favorited=models.Exists(favorite),
                             is_in_shopping_cart=models.Exists(shopping_cart))


class RecipeManager(models.Manager):

    def get_queryset(self):
        return (RecipeQuerySet(self.model)
                .with_related_data())
