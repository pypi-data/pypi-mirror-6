"""Interpolations for configparser.

All interpolations use ast.literal_eval to evalute Python literal
structures. With these interpolations it is possible to save and
recieve, for example, dictonaries from the config file without manually
processing it.

"""

from ast import literal_eval
from configparser import (Interpolation, BasicInterpolation,
                          ExtendedInterpolation)


class TypedInterpolationMixin:

    """Mixin class to use with interpolations."""

    def before_get(self, parser, section, option, value, defaults):
        """Use ast.literal_eval. Returns a python literal."""

        value = super().before_get(parser, section, option,
                                   value, defaults)

        try:
            return literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def before_set(self, parser, section, option, value):
        """Convert value to string automatically. Returns a string."""

        return super().before_set(parser, section, option, str(value))


class TypedInterpolation(TypedInterpolationMixin, Interpolation):

    """Interpolation that uses ast.literal_eval.

    The option values can contain Python literal structures.

    """

    pass


class TypedBasicInterpolation(TypedInterpolationMixin, BasicInterpolation):

    """Interpolation that uses BasicInterpolation and ast.literal_eval.

    The option values can contain Python literal structures.

    """

    pass


class TypedExtendedInterpolation(TypedInterpolationMixin,
                                 ExtendedInterpolation):

    """Interpolation that uses ExtendedInterpolation and ast.literal_eval.

    The option values can contain Python literal structures.

    """

    pass
