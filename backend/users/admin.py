from django.contrib import admin

from .models import User
from core.models import Follow


class FollowInline(admin.TabularInline):
    model = Follow
    fk_name = 'user'
    extra = 0


class UserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'email', 'last_name')
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', )
    inlines = [FollowInline]


admin.site.register(User, UserAdmin)
