from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    list_filter = ('email', 'username')
    search_fields = ('username',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    list_filter = ('user', 'author')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
