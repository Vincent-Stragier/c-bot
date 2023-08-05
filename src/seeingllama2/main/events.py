# -*- coding: utf-8 -*-
from __future__ import annotations

from flask import current_app, request
from flask_socketio import emit
from seeingllama2 import socketio
from seeingllama2.main.dialog_manager import DialogManager
from seeingllama2.main.interpreter import interpreter


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
        request_id=request.values.get("request_id", ""),
        connector=current_app.config["config"]["llm_api"]["name"],
        base_url=(
            f'{current_app.config["config"]["llm_api"]["url"]}:'
            f'{current_app.config["config"]["llm_api"]["port"]}'
        ),
        api_path=current_app.config["config"]["llm_api"]["path"],
    )

    bot_to_tool = dialog_manager.get_response(
        {
            "text_input": message,
            "origin": "user",
            "ghost_prompt": current_app.config["prompt"],
        }
    )

    # Send message to interpreter
    tool_to_bot = interpreter(bot_to_tool[-1].get("text", ""), run=True)

    # Send the message from tool to llm
    bot_to_user = dialog_manager.get_response(
        {
            "text_input": tool_to_bot,
            "origin": "tool",
            "ghost_prompt": current_app.config["prompt"],
        }
    )

    message = (
        f"Bot to tool: {bot_to_tool[-1].get('text', '')}"
        f"</br>Tool to bot: {tool_to_bot}"
        f"</br>Bot to user: {bot_to_user[-1].get('text', '')}"
    )

    print(message, bot_to_user)

    emit(
        "message",
        {
            "content": message,
            "end": True,
            "start": True,
            "bot_name": js_app_config.get("bot_name", "C-Bot"),
        },
        room=request.values.get("request_id", ""),
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
        room=request.values.get("request_id", ""),
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
