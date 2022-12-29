from django.urls import include, path
from rest_framework import routers

from .ingredients.views import IngredientViewSet
from .recipes.views import RecipeViewSet
from .tags.views import TagViewSet
from .users.views import CustomUserViewSet

app_name = 'api'

router_api = routers.DefaultRouter()

router_api.register('users', CustomUserViewSet)
router_api.register('tags', TagViewSet)
router_api.register('ingredients', IngredientViewSet)
router_api.register('recipes', RecipeViewSet)

djoser = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

urlpatterns = [
    path('', include(router_api.urls)),
    path('', include(djoser)),
]
