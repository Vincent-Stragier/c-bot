"""
    This programs allow to create specialised agent for visually impaired people.

    Copyright (C) 2023 Vincent STRAGIER (vincent.stragier@outlook.com)
"""
from __future__ import annotations

import os

import pkg_resources
import yaml
from eventlet import monkey_patch
from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO

from .voice import generate_sound_file
from .utils import setlocale

monkey_patch()

CONFIG_FILE = pkg_resources.resource_string(
    __name__, 'config/configuration.yaml')
PROMPT_FILE = pkg_resources.resource_string(__name__, 'config/prompt.txt')

app = Flask(__name__, )


def save_client_request(user_request: dict) -> bool:
    """Save the user request in an historic (SQL database).

    Args:
        user_request (dict): the user request

    Returns:
        bool: True if the request has been saved, False otherwise
    """
    # Save request in an historic (SQL database)
    print(f'{user_request = }')
    return False


def main() -> None:
    """Run the application.

    Returns:
        None: None
    """
    # generate a secret key for the session
    app.config['SECRET_KEY'] = os.urandom(24)

    # Load the configuration file
    app.config['config'] = yaml.load(CONFIG_FILE, Loader=yaml.FullLoader)

    # Let's set a non-US locale
    # setlocale('fr_FR.UTF-8')
    setlocale(app.config['config']['interface']['locale'])

    # Load the prompt file
    app.config['prompt'] = PROMPT_FILE.decode('utf-8')

    # Create a socketio instance
    socket_io = SocketIO(app, cors_allowed_origins='*', threaded=True)

    @ socket_io.on('message')
    def handle_message(message):
        """Handle a message from the websocket.

        Args:
            message (str): the message
        """
        voice_config = app.config['config']['voice']
        js_app_config = app.config['config']['js_app']

        socket_io.emit(
            'message', {'content': message, 'end': True, 'start': True,
                        'bot_name': js_app_config.get('bot_name', 'C-Bot')
                        }, room=request.sid)

        # Play the response on a specific websocket session
        socket_io.emit('speech', {'text': message,
                                  'voice': voice_config.get('id', 0),
                                  'rate': voice_config.get('rate', 200),
                                  'volume': voice_config.get('volume', 1)
                                  }, room=request.sid)

        # socket_io.emit(
        #     'message', {'content': '', 'end': True, 'start': False,
        #                 'bot_name': js_app_config.get('bot_name', 'C-Bot')
        #                 }, room=request.sid)

    @ socket_io.on('connect')
    def handle_connect():
        """Handle a connection to the websocket."""
        username = app.config['config']['js_app'].get('username', 'Anonymous')
        socket_io.emit('username', {'username': username}, room=request.sid)
        print(f'Client connected {request.sid = }')

    @ socket_io.on('disconnect')
    def handle_disconnect():
        """Handle a disconnection from the websocket."""
        print(f'Client disconnected {request.sid = }')

    socket_io.run(app, debug=True)


if __name__ == "__main__":
    import warnings

    MODULE = "c_bot"
    warnings.warn(
        f"use 'python -m {MODULE}', not 'python -m {MODULE}.{MODULE}'",
        DeprecationWarning)
