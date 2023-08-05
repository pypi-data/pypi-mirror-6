Interpolations for configparser.

All interpolations use ast.literal_eval to evalute Python literal
structures. With these interpolations it is possible to save and
recieve, for example, dictonaries from the config file without manually
processing it.
