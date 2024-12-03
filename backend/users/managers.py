from django.contrib.auth.models import UserManager
from django.db import models


class UserQuerySet(models.QuerySet, UserManager):

    def with_related_data(self):
        return self.prefetch_related('follower', 'recipes')

    def is_subscribe(self, user):
        return self.annotate(is_subscribed=models.Exists(
            user.follower.filter(following=models.OuterRef('pk'))))