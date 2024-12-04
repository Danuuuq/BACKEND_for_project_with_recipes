from django.contrib.auth.models import UserManager
from django.db import models


class UserQuerySet(models.QuerySet, UserManager):

    def with_related_data(self):
        return self.prefetch_related('followers', 'recipes')

    def is_subscribe(self, user):
        return self.annotate(is_subscribed=models.Exists(
            user.followers.filter(following=models.OuterRef('pk'))))
