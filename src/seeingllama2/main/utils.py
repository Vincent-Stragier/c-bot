"""The utils module contains utility functions the module uses."""
import locale
from multiprocessing import Lock
from contextlib import contextmanager

LOCALE_LOCK = Lock()


@contextmanager
def setlocale(name):
    """Set the locale.

    Args:
        name (str): the name of the locale

    Returns:
        None: None
    """
    with LOCALE_LOCK:
        fallback = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, fallback)
