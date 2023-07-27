import os

import pkg_resources
import yaml
from eventlet import monkey_patch
from flask import Flask
from flask_socketio import SocketIO

# from seeingllama2.main.utils import setlocale
# from flask_sqlalchemy import SQLAlchemy

socketio = SocketIO(cors_allowed_origins="*", threaded=True)

from seeingllama2.main import main as main_blueprint  # noqa: E402 isort:skip
from seeingllama2.main.utils import setlocale  # noqa: E402 isort:skip

monkey_patch()

CONFIG_FILE = pkg_resources.resource_string(
    __name__, "config/configuration.yaml")
PROMPT_FILE = pkg_resources.resource_string(__name__, "config/prompt.txt")

app = Flask(__name__, instance_relative_config=True)
app.config["SECRET_KEY"] = os.urandom(24)
# Load the configuration file
app.config["config"] = yaml.load(CONFIG_FILE, Loader=yaml.FullLoader)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///faces_database.sqlite'
# face_database = SQLAlchemy(app)

# Let's set a non-US locale
# setlocale('fr_FR.UTF-8')
setlocale(app.config["config"]["interface"]["locale"])

# Load the prompt file
app.config["prompt"] = PROMPT_FILE.decode("utf-8")

app.register_blueprint(main_blueprint)
