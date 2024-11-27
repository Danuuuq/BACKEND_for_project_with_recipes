from django.contrib import admin

from .models import (Recipe, Ingredient, RecipeIngredient,
                     RecipeTag, Favorite, PurchaseUser)
from .models import (Recipe, Ingredient, RecipeIngredient,
                     RecipeTag)


class FavoriteStackedInline(admin.StackedInline):
    model = Favorite
    fk = 'recipe'


class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'author')
    # list_filter = ('tag', )
    list_display = ('name', 'author')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(PurchaseUser)
admin.site.register(Favorite)
admin.site.register(RecipeTag)
