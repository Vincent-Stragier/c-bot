# -*- coding: utf-8 -*-
"""Main entry point for the application when run with the -m switch."""
import argparse

import yaml

from seeingllama2 import app, socketio, setlocale

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Seeing Llama 2")
    parser.add_argument("--config", "-c", type=str, help="Path to the config file")
    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        default="",
        help="Use the prompt file instead of the default text",
    )

    args = parser.parse_args()

    if args.config:
        # See __init__.py for the config loading
        app.config["config"].update(**yaml.load(args.config, Loader=yaml.FullLoader))
        app.debug = app.config["config"]["flask"].get("debug", False)

        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///faces_database.sqlite'
        # face_database = SQLAlchemy(app)

        setlocale(app.config["config"]["interface"]["locale"])

    if args.prompt:
        # Load the prompt file
        with open(args.prompt, "r", encoding="utf-8") as prompt_file:
            app.config["prompt"] = prompt_file.read()

    socketio.init_app(app, async_mode="eventlet")

    host = app.config["config"]["flask"].get("host", "localhost")
    port = app.config["config"]["flask"].get("port", 5000)

    ssl_keyfile = app.config["config"]["flask"].get("ssl_keyfile", None)
    ssl_certfile = app.config["config"]["flask"].get("ssl_certfile", None)

    # If we have a keyfile and a certfile, we are in HTTPS mode
    server_side_mode = True if ssl_keyfile and ssl_certfile else False
    print(f"Server side mode: {server_side_mode}")

    socketio_config = {
        "host": host,
        "port": port,
        "keyfile": ssl_keyfile,
        "certfile": ssl_certfile,
        "debug": app.debug,
        "server_side": server_side_mode,
    }

    if not server_side_mode:
        socketio_config.pop("keyfile")
        socketio_config.pop("certfile")
        socketio_config.pop("server_side")

    socketio.run(app, **socketio_config)

else:
    raise RuntimeError("Only for use with the -m switch, not as a Python API")
