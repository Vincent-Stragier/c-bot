# -*- coding: utf-8 -*-
"""Application routes."""
from flask import current_app, redirect, render_template, request, send_file

from . import main
from .voice import generate_sound_file


@main.before_request
def redirect_to_right_scheme():
    """Redirect to the HTTPS version if needed, otherwise to the HTTP version."""
    # print("before_request is working?")
    if current_app.env == "development":
        return
    if request.is_secure:
        return

    use_ssl = current_app.config["config"]["flask"].get("ssl", False)
    if request.url.startswith("http://") and use_ssl:
        # print("Redirecting to HTTPS")
        url = request.url.replace("http://", "https://", 1)
        # print(url)
        return redirect(url, code=301)

    if request.url.startswith("https://") and not use_ssl:
        # print("Redirecting to HTTP")
        url = request.url.replace("https://", "http://", 1)
        # print(url)
        return redirect(url, code=301)

    return


@main.route("/", methods=["GET"])
def index() -> str:
    # Needs to implement a mechanism to restore the previous session
    # if the user is already connected
    return render_template("index.htm", **current_app.config["config"]["html_index"])


@main.route("/a", methods=["GET"])
def generate_audio():
    """Generate an audio file from text.

    Returns:
        Response: the audio file
    """
    text = request.args.get("text", "")
    voice = int(request.args.get("voice", "0"))
    rate = float(request.args.get("rate", "200"))
    volume = float(request.args.get("volume", "1"))

    return send_file(
        generate_sound_file(text=text, voice=voice, rate=rate, volume=volume),
        download_name="sound.mp3",
    )
