from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import (Recipe, Ingredient, RecipeIngredient,
                     RecipeTag, Favorite, PurchaseUser, Tag)


class FavoriteStackedInline(admin.StackedInline):
    model = Favorite
    fk = 'recipe'
    extra = 0


class PurchaseStackedInline(admin.StackedInline):
    model = PurchaseUser
    fk = 'recipe'
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name__icontains', 'author__last_name__icontains')
    list_filter = ('tag__name', )
    list_display = ('name', 'author', 'count_favorite')
    inlines = [FavoriteStackedInline, PurchaseStackedInline]
    readonly_fields = ['count_favorite']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_favorite_count=Count('favorite'))
        return queryset

    def count_favorite(self, obj):
        return obj._favorite_count
    count_favorite.short_description = 'В избранном'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(PurchaseUser)
admin.site.register(Favorite)
admin.site.register(RecipeTag)
admin.site.register(Tag)
