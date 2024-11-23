# import random

# from django.conf import settings

# from .models import Recipe


# def create_short_link():
#     not_unique = True
#     while not_unique:
#         short_url = ''.join(
#             random.choices(settings.SYMBOLS_FOR_SHORT_URL,
#                            k=settings.MAX_LENGTH_SHORT_URL))
#         if not Recipe.objects.filter(short_url=short_url).exists():
#             not_unique = False
#     return short_url