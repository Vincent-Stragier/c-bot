"""
    This programs allow to create specialised agent for visually impaired people.

    Copyright (C) 2023 Vincent STRAGIER (vincent.stragier@outlook.com)
"""
from __future__ import annotations
import pyttsx3
from contextlib import contextmanager
from typing import Generic, TypeVar
from queue import Empty, Full
from multiprocessing import Process, Queue, Lock
# from time import sleep
import tempfile
import os
import logging
import locale
import json
import io
import asyncio
from eventlet import monkey_patch
monkey_patch()
# from __future__ import print_function
# from functools import partial
# import argparse
# import requests
# import socket
# import threading
# import traceback
# import pkg_resources
# import sys

# from datetime import datetime

# from .ner import ner

# Import text to speech engine
engine_tts = pyttsx3.init()

LOCALE_LOCK = Lock()


@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


# Let's set a non-US locale
# locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# From https://stackoverflow.com/a/75210864/10949679
T = TypeVar('T')


class AsyncQueue(Generic[T]):
    """Async wrapper for queue.Queue.

    Args:
        queue (Queue): the queue to wrap

    Attributes:

    SLEEP (float): the time to sleep when the queue is full or empty

    Methods:
        get: get an item from the queue

        put: put an item into the queue

        task_done: mark the item as done
    """

    SLEEP: float = 0.01

    def __init__(self, queue: Queue[T]):
        self._Q: Queue[T] = queue

    async def get(self) -> T:
        """Get an item from the queue.

        Returns:
            T: the item from the queue

        Raises:
            Empty: if the queue is empty
        """
        while True:
            try:
                return self._Q.get_nowait()
            except Empty:
                await asyncio.sleep(self.SLEEP)

    async def put(self, item: T) -> None:
        """Put an item into the queue.

        Args:
            item (T): the item to put into the queue

        Returns:
            None: None

        Raises:
            Full: if the queue is full
        """
        while True:
            try:
                self._Q.put_nowait(item)
                return None
            except Full:
                await asyncio.sleep(self.SLEEP)

    def task_done(self) -> None:
        """Mark the item as done.

        Returns:
            None: None
        """
        self._Q.task_done()
        return None

# class ManageVerbose:
#     """Allows to mask print() to the user."""

#     def __init__(self, verbose=True):
#         self.verbosity = verbose

#     def __enter__(self):
#         if not self.verbosity:
#             self._original_stdout = sys.stdout
#             sys.stdout = open(os.devnull, 'w')

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if not self.verbosity:
#             sys.stdout.close()
#             sys.stdout = self._original_stdout


def save_client_request(request: dict) -> bool:
    # TODO:
    # save request in an historic (SQL database)

    return False


def generate_answer(request: str, intent: str | None = None, ner: list | None = None) -> str:
    return "Le moteur de dialogue n'est pas encore implémenté."
    # match intent:
    #     case 'time':
    #         return 'Il est ' + datetime.today().strftime('%H heures %M minutes et %S secondes')
    #     case 'date':
    #         return 'Nous sommes le ' + datetime.today().strftime('%A %d %B %Y')
    #     case _:
    #         return f'"Réponse inconnue" ({intent = }, {ner = })'


def play(text: str, voice: int, rate: float, volume: float):
    """Play a text with the TTS engine.

    Args:
        text (str): the text to convert to speech and play
        voice (int): the voice to use
        rate (float): the rate of the speech (default is 200 words per minute)
        volume (float): the volume of the speech (default is 1.0)
    """
    voice = engine_tts.getProperty('voices')[voice]
    engine_tts.setProperty('voice', voice.id)
    engine_tts.setProperty('rate', rate)  # default is 200
    engine_tts.setProperty('volume', volume)
    engine_tts.say(text)
    engine_tts.runAndWait()


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
        engine_tts.setProperty('rate', rate)  # default is 200
        engine_tts.setProperty('volume', volume)
        file_name = 'sound.mp3'
        file_name = os.path.join(temp_dir, file_name)
        engine_tts.save_to_file(text, file_name)
        engine_tts.runAndWait()
        while not os.listdir(temp_dir):
            pass
        temp_file = io.BytesIO(open(file_name, 'rb').read())
    return temp_file


class _WebsocketClientProcess():
    """A websocket client process.

    Attributes:
        _sending_queue (AsyncQueue): the sending queue

    Methods:
        run: run the process
        start: start the process

    """

    def __init__(self) -> None:
        """Initialize the websocket client process.

        Args:
            None

        Returns:
            None: None
        """
        # super().__init__()
        pass

    async def run(self, address: str, request_sid: str, sending_queue: Queue) -> None:
        """A websocket process.

        Args:
            socket_io (Flask-SocketIO): the socket-io instance
            address (str): the address of the websocket server
        """
        from websockets import connect

        logging.basicConfig(
            format="%(asctime)s %(message)s",
            level=logging.WARN,
        )

        from flask_socketio import SocketIO

        # socket_io = SocketIO(message_queue='amqp://')

        # Create a websocket connection
        async with connect(address, logger=logging.getLogger('websocket.client')) as websocket:
            print(f'connected to websocket server: {address = }')
            # Initiate the connection
            await websocket.send(json.dumps({"type": "open_inference_session", "max_length": 1024}))

            # Send a test message
            # await websocket.send(json.dumps({
            #     "type": "generate",
            #     "inputs": f"La langue est source de beauté.\"",
            #     "max_new_tokens": 1,
            #     "extraStopSequences": ["\n\nHuman", "\n\nhuman"],
            #     "stop_sequence": "\n\n",
            #     "do_sample": 1,
            #     "top_k": 40,
            #     "temperature": 0.9
            # }))

            async def _receive_messages(websocket, socket_io, request_sid):
                """Receive messages from the websocket server.

                Args:
                    websocket (websockets.client.WebSocketClientProtocol): the websocket connection
                    socket_io (Flask-SocketIO): the socket-io instance (used to emit messages)
                    request_sid (str): the request sid
                """
                async for message in websocket:
                    message = json.loads(message)
                    if message['ok'] is False:
                        print(f'error: {message}')
                    else:
                        print(f'{message.get("outputs", "")}', end='')

                    # NOTE: not used for now
                    # socket_io.emit('message', json.dumps({
                    #     'message': message.get("outputs", ""),

                    # }), room=request_sid)

                    socket_io.emit(
                        'message', {
                            'content': message.get('outputs', ''),
                            'end': False,
                            'start': True
                        }, room=request_sid)
                    await asyncio.sleep(0)

            # Create a task to send messages to the websocket server
            async def _send_messages(websocket):
                """Send messages to the websocket server.

                Args:
                    websocket (websockets.client.WebSocketClientProtocol): the websocket connection
                """
                while True:
                    message = await sending_queue.get()
                    message = json.dumps({
                        "type": "generate",
                        "inputs": f"{message}\"",
                        "max_new_tokens": 1,
                        "extraStopSequences": ["\n\nHuman", "\n\nhuman"],
                        "stop_sequence": "\n\n",
                        "do_sample": 1,
                        "top_k": 40,
                        "temperature": 0.9})
                    print(f'got message to send! {message = } (send)')
                    await websocket.send(message)
                    await asyncio.sleep(0)

            # Start the task concurrently
            await asyncio.gather(
                _receive_messages(websocket, socket_io, request_sid),
                _send_messages(websocket),
            )

    def start(self, address: str, request_sid: str, sending_queue) -> None:
        """Start the websocket client process.

        Args:
            address (str): the address of the websocket server
            request_sid (str): the request sid
            sending_queue (Queue): the sending queue

        Returns:
            None: None
        """
        print(
            f'starting websocket client process... {address = } {request_sid = } {sending_queue = }')
        try:
            asyncio.run(self.run(address, request_sid, sending_queue))
        except KeyboardInterrupt:
            print('User stopped websocket client process')


def main() -> None:
    from flask import Flask, render_template, request, send_file
    from flask_socketio import SocketIO

    app = Flask(__name__, )
    # generate a secret key for the session
    app.config['SECRET_KEY'] = os.urandom(24)
    socket_io = SocketIO(app, cors_allowed_origins='*', threaded=True)

    # Open a websocket to communicate with the chatbot
    address = 'ws://chat.petals.ml/api/v2/generate'

    # Create a queue to keep a trace of the process and related id
    process_queue_dict_lock = Lock()
    process_queue_dict = {}

    # Define app routes
    @ app.route("/")
    def index() -> str:

        # Needs to implement a mechanism to restore the previous session
        # if the user is already connected
        return render_template(
            "index.htm", title='C-Bot',
            chat_title='Conversation avec l\'agent interactif',
            chat_number_of_messages="0 message",
            chat_send_button_value='Envoyer',
            chat_input_placeholder='Saisissez votre message ici',
            footer_text='© 2023 - Agent interactif de Vincent Stragier, Université de Mons et les Amis des Aveugles de Ghlin',
        )

    @ socket_io.on('message')
    def handle_message(message):
        """Handle a message from the websocket.

        Args:
            message (str): the message
        """
        # print(f'{message = }')
        # Do a simple echo
        # predicted_intents = chatbot.predict_class(message)
        # intent = predicted_intents[0]["intent"]
        # response = generate_answer(message, intent, ner(message))
        # response = generate_answer(message)
        # # Play the response on a specific websocket session
        # socket_io.emit('speech', {'text': response,
        #                           'voice': 0, 'rate': 200, 'volume': 100}, room=request.sid)
        # # Send the response to the websocket
        # socket_io.emit('message', f'{response}', room=request.sid)

        # Send message word by word
        socket_io.emit(
            'message', {'content': '', 'end': False, 'start': True}, room=request.sid)
        print(f'{message = }')

        process_queue_dict_lock.acquire()
        # Send message to process queue

        if request.sid in process_queue_dict:
            asyncio.run(process_queue_dict[request.sid][1].put(message))
        else:
            # Error
            print(f'Error: {request.sid} not in process_queue_dict')

        process_queue_dict_lock.release()

        # response = generate_answer(message)
        # ws.send(json.dumps({
        #     "type": "generate",
        #     "inputs": message,
        #     "max_new_tokens": 1,
        #     # extraStopSequences: ["\n\nHuman"],
        #     "stop_sequence": "\n\n",
        #     "do_sample": 1,
        #     "top_k": 40,
        #     "temperature": 0.9,} ))

        # words = response.split()
        # for word in words:
        #     socket_io.emit('message', {
        #                    'content': f'{word} ', 'end': False, 'start': False}, room=request.sid)
        #     sleep(0.2)

        socket_io.emit(
            'message', {'content': 'circa line 356', 'end': True, 'start': False}, room=request.sid)

        # # Play the response on a specific websocket session
        # socket_io.emit('speech', {'text': response,
        #                           'voice': 0, 'rate': 200, 'volume': 100}, room=request.sid)

    # handle session events

    @ socket_io.on('connect')
    def handle_connect():
        """Handle a connection to the websocket."""
        print(f'Client connected {request.sid = }')
        # Start the websocket process
        # websocket_process(socket_io, address)
        process_queue_dict_lock.acquire()

        message_queue = AsyncQueue(Queue())
        websocket_process = Process(
            target=_WebsocketClientProcess().start, args=(address, request.sid, message_queue))
        websocket_process.start()

        process_queue_dict[request.sid] = (websocket_process, message_queue)
        process_queue_dict_lock.release()

    @ socket_io.on('disconnect')
    def handle_disconnect():
        """Handle a disconnection from the websocket."""
        print(f'Client disconnected {request.sid = }')
        process_queue_dict_lock.acquire()

        websocket_process, message_queue = process_queue_dict[request.sid]
        websocket_process.terminate()
        websocket_process.join()

        del process_queue_dict[request.sid]
        process_queue_dict_lock.release()

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
        # print(f'{text = }, {voice = }, {rate = }, {volume = }')
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
