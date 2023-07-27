# from .c_bot import *  # noqa: F401,F403
from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes, events
