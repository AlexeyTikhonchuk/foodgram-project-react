from django.contrib import admin

from .models import AmountIngredient, FavoriteRecipe, Recipe, ShoppingList


class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('in_favorites',)
    list_display = (
        'name',
        'author'
    )
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    empty_value_display = '-пусто-'

    def in_favorites(self, instance):
        return instance.favorite_recipes.count()
    in_favorites.short_description = 'добавлен_в_избранное'


class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'amount'
    )
    list_filter = ('ingredient', 'amount')
    search_fields = ('ingredient',)
    empty_value_display = '-пусто-'


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(AmountIngredient, AmountIngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
