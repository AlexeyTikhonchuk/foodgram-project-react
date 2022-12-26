from io import StringIO

from django.contrib.auth.hashers import check_password
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (AmountIngredient, FavoriteRecipe, Ingredient,
                            Recipe, ShoppingList, Tag)
from users.models import Follow, User

from .filters import IngredientSearchFilterBackend, RecipeFilterBackend
from .permissions import RecipePermission
from .serializers import (CreateAndUpdateRecipeSerializer,
                          CreatePasswordSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer, UserSerializer)
from .utils import PageLimitPaginator, delete_old_ingredients


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPaginator

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = CreatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        username = request.user.username
        user = get_object_or_404(
            self.get_queryset(),
            username=username
        )
        if check_password(password, user.password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = self.get_queryset().filter(
            following__user=request.user
        ).order_by('pk')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, user_id):
        follow_author = get_object_or_404(User, pk=user_id)
        if follow_author != request.user and (
            not request.user.follower.filter(author=follow_author).exists()
        ):
            Follow.objects.create(
                user=request.user,
                author=follow_author
            )
            serializer = FollowSerializer(
                follow_author, context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, user_id):
        follow_author = get_object_or_404(User, pk=user_id)
        data_follow = request.user.follower.filter(author=follow_author)
        if data_follow.exists():
            data_follow.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_400_BAD_REQUEST)


class TagViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(TagViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilterBackend,)
    search_fields = ('^name', 'name')


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPaginator
    permission_classes = (RecipePermission,)
    filter_backends = (RecipeFilterBackend,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return CreateAndUpdateRecipeSerializer
        return RecipeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_old_ingredients(instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_list = AmountIngredient.objects.filter(
            recipes__shopping_list_recipes__user=request.user
        )
        shopping_list = shopping_list.values('ingredient').annotate(
            total_amount=Sum('amount')
        )
        shopping_cart_file = StringIO()
        for position in shopping_list:
            ingredient = get_object_or_404(
                Ingredient,
                pk=position['ingredient']
            )
            amount = position['total_amount']
            shopping_cart_file.write(
                f' - {ingredient.name.title()}'
                f' ({ingredient.measurement_unit})'
                f' - {amount}' + '\n'
            )
        response = HttpResponse(
            shopping_cart_file.getvalue(),
            content_type='text'
        )
        response['Content-Disposition'] = (
            'attachment; filename="%s"' % 'shopping_list.txt'
        )
        return response


class ShoppingCartViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, id):
        recipe = get_object_or_404(Recipe, pk=id)
        queryset = getattr(recipe, 'shopping_list_recipes')
        if not queryset.filter(
            user=request.user
        ).exists():
            ShoppingList.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = ShortRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id):
        recipe = get_object_or_404(Recipe, pk=id)
        queryset = getattr(recipe, 'shopping_list_recipes')
        data = (
            queryset.filter(
                user=request.user
            )
        )
        if data.exists():
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class FavoriteViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, id):
        recipe = get_object_or_404(Recipe, pk=id)
        queryset = getattr(recipe, 'favorite_recipes')
        if not queryset.filter(
            user=request.user
        ).exists():
            FavoriteRecipe.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = ShortRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id):
        recipe = get_object_or_404(Recipe, pk=id)
        queryset = getattr(recipe, 'favorite_recipes')
        data = (
            queryset.filter(
                user=request.user
            )
        )
        if data.exists():
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
