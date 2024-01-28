from django.db.models import F, Q
from django.db.models.functions import Cast
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser

from cooking_book.seriaizer import *
from inspectors.schema_inspector import *
from inspectors.error_handler_inspector import ErrorInspector
from inspectors.data_validate_inspector import compare_objects_identity


ERROR: typing.Final[ErrorInspector] = ErrorInspector()


class RecipeView(ViewSet):
    queryset: typing.Final = Recipe.objects.all()

    def list(self, request) -> JsonResponse:
        return JsonResponse(
            data=RecipeSerializer(
                Recipe.objects.all(),
                many=True,
            ).data,
            status=status.HTTP_200_OK,
            safe=False,
        )

    def create(self, request) -> JsonResponse:
        recipe: typing.Dict[str, typing.Any] = JSONParser().parse(request)

        """
        сравниваем форму отправленную от клиентам с правильной формой
        """
        check, e = compare_objects_identity(
            form=recipe,
            right_form=recipe_model_json,
        )

        """
        если объект правильно составлен, то дальше уже сохраняем в БД
        """
        if check:
            recipe_serializer = RecipeSerializer(data=recipe)

            if recipe_serializer.is_valid(raise_exception=True):
                recipe_serializer.save()

            return JsonResponse(
                data=recipe_serializer.data, status=status.HTTP_201_CREATED, safe=False
            )

        return JsonResponse(
            data={"message": f"Wrong format of request: {e}"},
            status=status.HTTP_400_BAD_REQUEST,
            safe=False,
        )

    def update(self, request, pk=None) -> JsonResponse:
        recipe: typing.Final[Recipe] = get_object_or_404(self.queryset, pk=pk)

        if (
            updated_recipe := RecipeSerializer(recipe, data=JSONParser().parse(request))
        ).is_valid(raise_exception=True):
            updated_recipe.save()  # сохраняем изменения
            return JsonResponse(
                data=updated_recipe.data,
                safe=False,
                status=status.HTTP_200_OK,
            )

    @action(
        detail=False,
        methods=["GET"],
        description="""
        show_recipes_without_product с параметром product_id.
        Функция возвращает HTML страницу, на которой размещена таблица.
        В таблице отображены id и названия всех рецептов, в которых указанный продукт отсутствует,
        или присутствует в количестве меньше 10 грамм.
        """,
    )
    def show_recipes_without_product(self, request) -> JsonResponse:
        product_id: int = request.GET.get("product_id")

        if not product_id:
            return ERROR.get_response(
                message="product_id was not initiated",
                api_status=status.HTTP_400_BAD_REQUEST,
            )

        """
        находим Продукт из БД
        """
        product: typing.Final[Product] = get_object_or_404(
            Product.objects.all(),
            pk=product_id,
        )

        allowed_grams: typing.Final[list[str]] = list(
            map(lambda x: f"{x}g", range(1, 11))
        )

        recipe_list: typing.Final[list[Recipe]] = Recipe.objects.annotate(
            name_text=Cast(
                F("product_list__" + product.product_name), models.TextField()
            )
        ).filter(
            ~Q(
                product_list__has_key=product.product_name,
            )
            | Q(name_text__in=allowed_grams)
        )

        return JsonResponse(
            data=RecipeSerializer(
                recipe_list,
                many=True,
            ).data,
            status=status.HTTP_200_OK,
            safe=False,
        )

    @action(
        detail=False,
        methods=["GET"],
        description="""
        cook_recipe c параметром recipe_id.
        Функция увеличивает на единицу количество приготовленных блюд для каждого продукта,
        входящего в указанный рецепт.
        """,
    )
    def cook_recipe(self, request) -> JsonResponse:
        recipe_id: int = request.GET.get("recipe_id")

        if not recipe_id:
            return ERROR.get_response(
                message="recipe_id was not initiated",
                api_status=status.HTTP_400_BAD_REQUEST,
            )

        """
        находим нужный Рецепт
        """
        recipe: typing.Final[Recipe] = get_object_or_404(
            self.queryset,
            pk=recipe_id,
        )

        """
        фильтруем базу по названием продуктов для данного рецепта
        и обновляем счетчик для каждого продукта
        """
        Product.objects.filter(
            product_name__in=list(recipe.product_list.keys()),
        ).update(product_was_used_counter=F("product_was_used_counter") + 1)

        return JsonResponse(
            data={
                "message": "Recipe was updated successfully",
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["GET"],
        description="""
         add_product_to_recipe с параметрами recipe_id, product_id, weight.
         Функция добавляет к указанному рецепту указанный продукт с указанным весом.
         Если в рецепте уже есть такой продукт, то функция должна поменять его вес в этом рецепте на указанный.
        """,
    )
    def add_product_to_recipe(self, request, *args, **kwargs) -> JsonResponse:
        weight: str | None = request.GET.get("weight")

        if not weight:
            return ERROR.get_response(
                message="weight param was not initiated",
                api_status=status.HTTP_400_BAD_REQUEST,
            )

        recipe_id: int | None = request.GET.get("recipe_id")

        if not recipe_id:
            return ERROR.get_response(
                message="recipe_id param was not initiated",
                api_status=status.HTTP_400_BAD_REQUEST,
            )

        product_id: int | None = request.GET.get("product_id")

        if not product_id:
            return ERROR.get_response(
                message="product_id param was not initiated",
                api_status=status.HTTP_400_BAD_REQUEST,
            )

        """
        находим Продукт из БД
        """
        product: typing.Final[Product] = get_object_or_404(
            Product.objects.all(),
            pk=product_id,
        )

        """
        находим Рецепт из БД
        """
        recipe: typing.Final[Recipe] = self.queryset.get(pk=recipe_id)

        """
        добавляем или обновляем данные о граммаже продукта для рецепта
        """
        recipe.product_list[product.product_name] = weight

        """
        сохраняем обновленные данные в БД
        """
        recipe.save()

        return JsonResponse(
            data={
                "message": "Recipe was updated successfully",
            },
            status=status.HTTP_200_OK,
        )


class ProductView(ViewSet):
    queryset = Product.objects.all()

    def list(self, request) -> JsonResponse:
        return JsonResponse(
            data=ProductSerializer(
                Product.objects.all(),
                many=True,
            ).data,
            status=status.HTTP_200_OK,
            safe=False,
        )

    def create(self, request) -> JsonResponse:
        product: typing.Dict[str, typing.Any] = JSONParser().parse(request)

        """
        сравниваем форму отправленную от клиента с правильной формой
        """
        check, e = compare_objects_identity(
            form=product,
            right_form=product_model_json,
        )

        """
        если объект правильно составлен, то дальше уже сохраняем в БД
        """
        if check:
            product_serializer = ProductSerializer(data=product)

            if product_serializer.is_valid(raise_exception=True):
                product_serializer.save()

            return JsonResponse(
                data=product_serializer.data, status=status.HTTP_201_CREATED, safe=False
            )

        return JsonResponse(
            data={
                "message": f"Wrong format of request: {e}",
            },
            status=status.HTTP_400_BAD_REQUEST,
            safe=False,
        )

    def update(self, request, pk=None) -> JsonResponse:
        product: typing.Final[Product] = get_object_or_404(self.queryset, pk=pk)

        if (
            updated_product := ProductSerializer(
                product, data=JSONParser().parse(request)
            )
        ).is_valid(raise_exception=True):
            updated_product.save()  # сохраняем изменения
            return JsonResponse(
                data=updated_product.data,
                safe=False,
                status=status.HTTP_200_OK,
            )
