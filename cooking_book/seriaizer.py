from .models import *
from rest_framework import serializers

from constants.default_values import DefaultValues
from inspectors.data_validate_inspector import check_str


class RecipeSerializer(serializers.ModelSerializer):
    recipe_name: str = serializers.CharField(
        max_length=DefaultValues.max_text_length.value,
        min_length=DefaultValues.min_text_length.value,
        validators=[
            check_str,
        ],
        allow_blank=False,
        allow_null=False,
    )

    product_list: dict = serializers.DictField(
        allow_null=False,
        default={},
    )

    class Meta:
        model = Recipe
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    product_name: str = serializers.CharField(
        max_length=DefaultValues.max_text_length.value,
        min_length=DefaultValues.min_text_length.value,
        allow_blank=False,
        allow_null=False,
        validators=[
            check_str,
        ],
    )

    product_was_used_counter: int = serializers.IntegerField(
        allow_null=False,
        default=0,
    )

    class Meta:
        model = Product
        fields = "__all__"
