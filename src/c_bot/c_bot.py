"""
    This programs allow to create specialised agent for visually impaired people.

    Copyright (C) 2023 Vincent STRAGIER (vincent.stragier@outlook.com)
"""
from __future__ import annotations

import io
import locale
import os
import tempfile
from contextlib import contextmanager
from multiprocessing import Lock

import pkg_resources
import pyttsx4
import yaml
from eventlet import monkey_patch
from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO

monkey_patch()

# Import text to speech engine
engine_tts = pyttsx4.init()

LOCALE_LOCK = Lock()

CONFIG_FILE = pkg_resources.resource_string(
    __name__, 'config/configuration.yaml')
PROMPT_FILE = pkg_resources.resource_string(__name__, 'config/prompt.txt')


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


def generate_answer(user_request: str, intent: str | None = None, ner: list | None = None) -> str:
    """Generate an answer from a user request.

    Args:
        user_request (str): the user request
        intent (str): the intent of the user request
        ner (list): the named entities of the user request

    Returns:
        str: the answer
    """
    print(f'{user_request = } {intent = } {ner = }')
    return "Le moteur de dialogue n'est pas encore implémenté."


def generate_sound_file(text: str, voice: int, rate: float, volume: float) -> io.BytesIO:
    """Generate a sound file from text.

    Args:
        text (str): the text to convert to speech
        voice (int): the voice to use
        rate (float): the rate of the speech (default is 200 words per minute)
        volume (float): the volume of the speech (default is 1.0)

    Returns:
        BytesIO: the sound file
    """
    temp_file = io.BytesIO()
    with tempfile.TemporaryDirectory() as temp_dir:

        voice = engine_tts.getProperty('voices')[voice]
        engine_tts.setProperty('voice', voice.id)
        # Default is 200 words per minute
        engine_tts.setProperty('rate', rate)
        engine_tts.setProperty('volume', volume)
        file_name = 'sound.mp3'
        file_name = os.path.join(temp_dir, file_name)
        engine_tts.save_to_file(text, file_name)
        engine_tts.runAndWait()

        while not os.listdir(temp_dir):
            # Wait for the file to be created
            pass

        with open(file_name, 'rb') as audio_file:
            temp_file = io.BytesIO(audio_file.read())

    return temp_file


def main() -> None:
    """Run the application.

    Returns:
        None: None
    """
    app = Flask(__name__, )
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

    # Define app routes
    @ app.route("/")
    def index() -> str:
        # Needs to implement a mechanism to restore the previous session
        # if the user is already connected
        return render_template(
            "index.htm", **app.config['config']['html_index'])

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

    @ app.route('/a')
    def generate_audio():
        """Generate an audio file from text.

        Returns:
            Response: the audio file
        """
        text = request.args.get('text', '')
        voice = int(request.args.get('voice', '0'))
        rate = float(request.args.get('rate', '200'))
        volume = float(request.args.get('volume', '1'))

        return send_file(generate_sound_file(
            text=text, voice=voice, rate=rate, volume=volume),
            download_name='sound.mp3')

    socket_io.run(app, debug=True)


if __name__ == "__main__":
    import warnings

    MODULE = "c_bot"
    warnings.warn(
        f"use 'python -m {MODULE}', not 'python -m {MODULE}.{MODULE}'",
        DeprecationWarning)
