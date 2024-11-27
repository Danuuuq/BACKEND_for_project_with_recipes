from django.db.models import Sum
from django.http import HttpResponse

from .models import Ingredient


def create_shopping_cart(user):
    """Формирование списка покупок пользователя."""
    ingredients = (Ingredient.objects
                   .filter(ingredientrecipe__recipe__purchase__user=user)
                   .annotate(total_amount=Sum('ingredientrecipe__amount')))

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.txt"')

    lines = []
    lines.append("Список покупок:\n")

    for ingredient in ingredients:
        line = (
            f'{ingredient.name}: {ingredient.total_amount}'
            f'{ingredient.measurement_unit}'
            ' | Добавлено в корзину: [ ]\n')
        lines.append(line)

    response.writelines(lines)

    return response
