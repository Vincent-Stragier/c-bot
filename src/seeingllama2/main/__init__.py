from flask import Blueprint

main = Blueprint("main", __name__)

from . import events, routes  # noqa: E402, F401 isort:skip
