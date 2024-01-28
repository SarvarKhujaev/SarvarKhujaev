import typing
from typing import Any

from cerberus import Validator
from inspectors.error_handler_inspector import ErrorInspector


ERROR: typing.Final[ErrorInspector] = ErrorInspector()


def check_str(message: str):
    if message is None or len(message) < 3:
        ERROR.raise_error(message="param cannot be empty")


"""
сравнивает 2 объекта на идентичность с помощью Cerberus
"""


def compare_objects_identity(
    form: typing.Dict[str, typing.Any],  # принятая форма
    right_form: typing.Dict[str, typing.Any],  # то как она должна быть
    required_all: bool = True,
) -> tuple[bool, Any]:  # правильная форма для сравнения
    validator: typing.Final[Validator] = Validator(
        required_all=required_all, allow_unknown=True
    )
    return validator.validate(form, right_form), validator.errors
