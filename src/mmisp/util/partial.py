from types import UnionType
from typing import Any, Type, get_args, get_origin, get_type_hints

from pydantic import BaseModel, Field, create_model

partial_model_registry: dict[str, Type[BaseModel]] = {}


def _is_pydantic_base_model(type_: Type) -> bool:
    """Check if the type is a subclass of BaseModel."""
    try:
        return issubclass(type_, BaseModel)
    except TypeError:
        return False


def _make_optional(type_: Type) -> Any:
    """Make the type optional."""
    origin = get_origin(type_)
    args = get_args(type_)

    if origin is not None and origin is not UnionType:
        # origin is generic, make each argument optional recursively
        new_args = tuple(_make_optional(arg) for arg in args)
        # reconstruct the type with its arguments, now optional
        return origin[new_args] | None
    elif _is_pydantic_base_model(type_):
        # makes the Pydantic model fields optional recursively
        return partial(type_) | None
    else:
        return type_ | None


def partial(model: Type[BaseModel]) -> Type[BaseModel]:  # type: ignore
    """Takes a Pydantic model and returns a modified version with every field as optional."""
    new_name = "Partial" + model.__name__

    if partial_model_registry.get(new_name):
        return partial_model_registry[new_name]

    fields = {}

    for field_name, model_field in model.__fields__.items():
        field_type = get_type_hints(model).get(field_name, model_field.outer_type_)
        optional_field_type = _make_optional(field_type)

        default_value = None

        # check if the field has a default value
        if model_field.default is not None:
            default_value = model_field.default
        elif model_field.default_factory is not None:
            default_value = Field(default_factory=model_field.default_factory)

        fields[field_name] = (optional_field_type, default_value)

    partial_model_registry[new_name] = create_model(new_name, **fields)  # type: ignore
    return partial_model_registry[new_name]


def _print_model_attributes(model_cls: Type[BaseModel], indent: int = 0) -> None:
    """developer tool: prints model attributes"""
    indent_str = " " * indent
    print(f"{indent_str}{model_cls.__name__}:")
    for name, field in model_cls.__fields__.items():
        field_type = field.type_
        default = field.default

        try:
            if issubclass(field_type, BaseModel):
                print(f"{indent_str}  {name}: (Nested Model) Allow_None: {field.allow_none}")
                _print_model_attributes(field_type, indent + 4)
            else:
                print(f"{indent_str}  {name}: {field_type} (default: {default}) Allow_None: {field.allow_none}")
        except Exception:
            print(f"{indent_str}  {name}: {field_type} (default: {default}) Allow_None: {field.allow_none}")
