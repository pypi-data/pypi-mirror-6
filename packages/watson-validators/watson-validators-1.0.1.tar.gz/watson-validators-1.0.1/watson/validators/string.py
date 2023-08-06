# -*- coding: utf-8 -*-
import re
from watson.validators import abc


class Length(abc.Validator):

    """Validates the length of a string.

    Example:

    .. code-block:: python

        validator = Length(1, 10)
        validator('Test')  # True
        validator('Testing maximum')  # raises ValueError
    """

    def __init__(self, min=-1, max=-1,
                 message='"{value}" does not meet the required length'):
        """Initializes the validator.

        Min, max, length are interpolated into the message.

        Args:
            min (int): The minimum length of the string.
            max (int): The maximum length of the string.
            message (string): The message to be used if the validator fails.
        """
        self.message = message
        if max > -1 and min > max:
            raise ValueError('Min cannot be greater than max')
        self.min = int(min)
        self.max = int(max)

    def __call__(self, value):
        valid = True
        message = None
        if not value:
            raise ValueError(self.message.format(
                min=self.min,
                max=self.max,
                value=value,
                length=0))
        str_len = len(value)
        if (self.min > -1 and str_len < self.min) or (self.max > -1 and str_len > self.max):
            valid = False
            message = self.message.format(
                min=self.min,
                max=self.max,
                value=value,
                length=str_len)
        if not valid:
            raise ValueError(message)
        return valid


class Required(abc.Validator):

    """Validates whether or not a value exists.

    Example:

    .. code-block:: python

        validator = Required()
        validator('Test')  # True
        validator('')  # raises ValueError
    """

    def __init__(self, message='Value is required'):
        self.message = message

    def __call__(self, value):
        if not value:
            raise ValueError(self.message.format(value=value))
        return True


class RegEx(abc.Validator):

    """Validates a value based on a regular expression.

    Example:

    .. code-block:: python

        validator = RegEx('Match')
        validator('Match')  # True
        validator('Other')  # raises ValueError
    """

    def __init__(self, regex, flags=0,
                 message='"{value}" does not match pattern "{pattern}"'):
        if isinstance(regex, str):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message

    def __call__(self, value):
        if not self.regex.match(value):
            raise ValueError(
                self.message.format(
                    value=value,
                    pattern=self.regex.pattern))


class Csrf(abc.Validator):

    """Validates a csrf token.

    Example:

    .. code-block:: python

        validator = Csrf()
        validator('submitted token')
    """

    def __init__(self, token=None,
                 message='Cross-Site request forgery attempt detected, invalid token specified "{token}"'):
        self.token = token
        self.message = message

    def __call__(self, value):
        if value != self.token:
            raise ValueError(self.message.format(token=value))
