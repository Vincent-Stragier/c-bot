# from .c_bot import *  # noqa: F401,F403

from . import routes, events
from flask import Blueprint

main = Blueprint('main', __name__)
