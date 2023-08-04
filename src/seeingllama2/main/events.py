# -*- coding: utf-8 -*-
from __future__ import annotations

from flask import current_app, request
from flask_socketio import emit
from seeingllama2 import socketio
from seeingllama2.main.dialog_manager import DialogManager


@socketio.on("message")
def handle_message(message):
    """Handle a message from the websocket.

    Args:
        message (str): the message
    """
    voice_config = current_app.config["config"]["voice"]
    js_app_config = current_app.config["config"]["js_app"]

    # Send the message to the dialog manager
    dialog_manager = DialogManager(
        request_id=request.sid,
        connector=current_app.config["config"]["llm_api"]["name"],
        base_url=(
            f'{current_app.config["config"]["llm_api"]["url"]}:'
            f'{current_app.config["config"]["llm_api"]["port"]}'
        ),
        api_path=current_app.config["config"]["llm_api"]["path"],
    )

    response = dialog_manager.get_response(f"<user>{message}</user>")

    print(f"Response: {response}")

    emit(
        "message",
        {
            "content": response,
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
            "text": response,
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
    username = current_app.config["config"]["js_app"].get(
        "username", "Anonymous"
    )
    emit("username", {"username": username}, room=request.sid)
    print(f"Client connected {request.sid = }")


@socketio.on("disconnect")
def handle_disconnect():
    """Handle a disconnection from the websocket."""
    print(f"Client disconnected {request.sid = }")
