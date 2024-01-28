from django.db import models
from django.db.models import JSONField

from constants.default_values import DefaultValues
from inspectors.data_validate_inspector import check_str


class Product(models.Model):
    id: models.AutoField = models.AutoField(
        primary_key=True,
        auto_created=True,
    )

    product_name: str = models.CharField(
        validators=[check_str],
        max_length=DefaultValues.max_text_length.value,
        editable=False,
        blank=False,
        null=False,
    )

    """
    целочисленное поле, хранящее информацию о том,
    сколько раз было приготовлено блюдо с использованием этого продукта.
    """
    product_was_used_counter: int = models.IntegerField(
        default=0,
        blank=False,
        null=False,
    )


class Recipe(models.Model):
    id: models.AutoField = models.AutoField(
        primary_key=True,
        auto_created=True,
    )

    recipe_name: str = models.CharField(
        max_length=DefaultValues.max_text_length.value,
        validators=[check_str],
        editable=False,
        blank=False,
        null=False,
    )

    """
    набор входящих в рецепт продуктов, с указанием веса в граммах
    """
    product_list: dict[str, str] = JSONField(
        default=dict,
    )
