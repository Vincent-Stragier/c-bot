from __future__ import annotations


# from flask import session
from flask_socketio import emit  # , join_room, leave_room
from flask import request, current_app
from seeingllama2 import socketio


@socketio.on("message")
def handle_message(message):
    """Handle a message from the websocket.

    Args:
        message (str): the message
    """
    voice_config = current_app.config["config"]["voice"]
    js_app_config = current_app.config["config"]["js_app"]

    emit(
        "message",
        {
            "content": message,
            "end": True,
            "start": True,
            "bot_name": js_app_config.get("bot_name", "C-Bot"),
        },
        room=request.sid,
    )

    # Play the response on a specific websocket session
    emit(
        "speech",
        {
            "text": message,
            "voice": voice_config.get("id", 0),
            "rate": voice_config.get("rate", 200),
            "volume": voice_config.get("volume", 1),
        },
        room=request.sid,
    )

    # socketio.emit(
    #     'message', {'content': '', 'end': True, 'start': False,
    #                 'bot_name': js_app_config.get('bot_name', 'C-Bot')
    #                 }, room=request.sid)


@socketio.on("connect")
def handle_connect():
    """Handle a connection to the websocket."""
    username = current_app.config["config"]["js_app"].get("username", "Anonymous")
    emit("username", {"username": username}, room=request.sid)
    print(f"Client connected {request.sid = }")


@socketio.on("disconnect")
def handle_disconnect():
    """Handle a disconnection from the websocket."""
    print(f"Client disconnected {request.sid = }")
