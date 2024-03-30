""" Error classes for jsonlogic """


class JsonLogicError(Exception):
    """top-level error for JsonLogic"""


class JsonLogicArgumentError(JsonLogicError):
    """raised when there is a problem with an argument to an expression."""
