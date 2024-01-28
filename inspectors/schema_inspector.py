import typing
from constants.default_values import DefaultValues


recipe_model_json: typing.Dict[str, typing.Any] = {
    "recipe_name": {
        "type": "string",
        "empty": False,
        "required": True,
        "maxlength": DefaultValues.max_text_length.value,
        "minlength": DefaultValues.min_text_length.value,
    },
    "product_list": {
        "type": "dict",
        "empty": False,
        "required": True,
        "keysrules": {
            "type": "string",
            "required": True,
            "empty": False,
            "minlength": DefaultValues.min_text_length.value,
        },
        "valuesrules": {
            "type": "string",
            "required": True,
            "empty": False,
            "minlength": DefaultValues.min_text_length.value,
        },
    },
}

product_model_json: typing.Dict[str, typing.Any] = {
    "product_name": {
        "type": "string",
        "empty": False,
        "required": True,
        "maxlength": DefaultValues.max_text_length.value,
        "minlength": DefaultValues.min_text_length.value,
    },
}
