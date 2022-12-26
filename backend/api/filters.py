from rest_framework import filters


class IngredientSearchFilterBackend(filters.SearchFilter):
    search_param = 'name'
