import functools
import logging
from flask import Response
from flask_sqlalchemy import BaseQuery


logging.basicConfig(filename="logs.log", level=logging.DEBUG)


def debug(func):
    """Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        logging.debug(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)

        if isinstance(value, BaseQuery):
            logging.debug(f"{func.__name__!r} returned Base {value.all()}")
        elif isinstance(value, Response):
            logging.debug(f"{func.__name__!r} returned {value.get_data()}")
        else:
            logging.debug(f"{func.__name__!r} returned {value!r}")
        return value

    return wrapper_debug
