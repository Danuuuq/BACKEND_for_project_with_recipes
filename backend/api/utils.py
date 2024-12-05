from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import Ingredient


def create_shopping_cart(user):
    """Формирование списка покупок пользователя."""
    ingredients = (Ingredient.objects
                   .filter(ingredient_recipe__recipe__purchases__user=user)
                   .annotate(total_amount=Sum('ingredient_recipe__amount')))

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.txt"')

    lines = []
    lines.append("Список покупок:\n")

    for ingredient in ingredients:
        line = (
            f'{ingredient.name}: {ingredient.total_amount}'
            f'{ingredient.measurement_unit}'
            ' | Куплено: [ ]\n')
        lines.append(line)

    response.writelines(lines)

    return response
