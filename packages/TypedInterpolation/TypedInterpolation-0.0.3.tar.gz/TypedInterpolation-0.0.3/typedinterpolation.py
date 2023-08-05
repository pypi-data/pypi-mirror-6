"""Interpolations for configparser.

All interpolations use ast.literal_eval to evalute Python literal
structures. With these interpolations it is possible to save and
recieve, for example, dictonaries from the config file without manually
processing it.

"""

from ast import literal_eval as _literal_eval
from configparser import Interpolation as _Interpolation
from configparser import BasicInterpolation as _BasicInterpolation
from configparser import ExtendedInterpolation as _ExtendedInterpolation


def _eval(parser, value):

    try:
        return parser._convert_to_boolean(value)
    except ValueError:
        try:
            return _literal_eval(value)
        except (ValueError, SyntaxError):
            return value


class TypedInterpolation(_Interpolation):

    """Interpolation that uses ast.literal_eval.

    The option values can contain Python literal structures.

    """

    def before_get(self, parser, section, option, value, defaults):
        """The before_get method. Returns a python type."""

        value = super().before_get(self, parser, section, option,
                                   value, defaults)
        return _eval(parser, value)


class TypedBasicInterpolation(_BasicInterpolation):

    """Interpolation that uses BasicInterpolation and ast.literal_eval.

    The option values can contain Python literal structures.

    """

    def before_get(self, parser, section, option, value, defaults):
        """The before_get method. Returns a python type."""

        value = super().before_get(self, parser, section, option,
                                   value, defaults)
        return _eval(parser, value)


class TypedExtendedInterpolation(_ExtendedInterpolation):

    """Interpolation that uses ExtendedInterpolation and ast.literal_eval.

    The option values can contain Python literal structures.

    """

    def before_get(self, parser, section, option, value, defaults):
        """The before_get method. Returns a python type."""

        value = super().before_get(self, parser, section, option,
                                   value, defaults)
        return _eval(parser, value)
