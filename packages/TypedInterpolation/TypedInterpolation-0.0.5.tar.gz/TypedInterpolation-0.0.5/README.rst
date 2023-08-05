Interpolations for configparser.

TypedInterpolation provides additional `interpolations
<http://docs.python.org/3/library/configparser.html#interpolation-of-values>`_
for the configparser module.

All the provided interpolations use ast.literal_eval to convert
strings to Python literal structures. Also, when setting an option, the value
is automatically converted to a string.

Docs: `Read the docs <http://typedinterpolation.readthedocs.org/en/latest/>`_
