# -*- coding: utf-8 -*-
"""OobaboogaConnector class."""
import requests
from requests.auth import HTTPBasicAuth

from flask import current_app

DEFAULT_PARAMS = {
    "user_input": "",
    "max_new_tokens": 800,
    "history": {"internal": [], "visible": []},
    "mode": "chat",  # Valid options: 'chat', 'chat-instruct', 'instruct'
    "character": "Example",
    # 'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
    # 'context_instruct': '',  # Optional
    "your_name": "You",
    "regenerate": False,
    "_continue": False,
    "stop_at_newline": False,
    "chat_generation_attempts": 1,
    # "chat-instruct_command": (
    #     "Continue the chat dialogue below. "
    #     'Write a single reply for the character "<|character|>".\n\n<|prompt|>'
    # ),
    # Generation params. If 'preset' is set to different than 'None', the values
    # in presets/preset-name.yaml are used instead of the individual numbers.
    "preset": "None",
    "do_sample": True,
    "temperature": 0.6,
    "top_p": 0.9,
    "typical_p": 1,
    "epsilon_cutoff": 0,  # In units of 1e-4
    "eta_cutoff": 0,  # In units of 1e-4
    "tfs": 1,
    "top_a": 0,
    "repetition_penalty": 1.18,
    "repetition_penalty_range": 0,
    "top_k": 40,
    "min_length": 0,
    "no_repeat_ngram_size": 0,
    "num_beams": 1,
    "penalty_alpha": 0,
    "length_penalty": 1,
    "early_stopping": False,
    "mirostat_mode": 0,
    "mirostat_tau": 5,
    "mirostat_eta": 0.1,
    "seed": -1,
    "add_bos_token": True,
    "truncation_length": 2048,
    "ban_eos_token": False,
    "skip_special_tokens": True,
    "stopping_strings": [],
}


class OobaboogaConnector:
    """Class for connecting to OobaBooga."""

    def __init__(self, base_url="http://127.0.0.1:7860", api_path="/api/v1/chat"):
        """Initialize OobaBoogaConnector."""
        self.url = base_url + api_path
        self.params = DEFAULT_PARAMS
        self.basic_auth = False

        if current_app.config["config"]["llm_api"].get("http_basic_auth", False):
            self.basic_auth = True
            self.username = current_app.config["config"]["llm_api"]["http_basic_auth"][
                "username"
            ]
            self.password = current_app.config["config"]["llm_api"]["http_basic_auth"][
                "password"
            ]

    def set_params(self, params: dict):
        """Set the parameters.

        Args:
            params (dict): the parameters.
        """
        self.params = params

    def get_response(self, user_input: str, chat_history: dict | None = None):
        """Send a request to OobaBooga.

        Args:
            user_input (str): the user input.
            history (dict, optional): the history. Defaults to None.

        Returns:
            requests.Response: the response.
        """

        if chat_history is None:
            chat_history = {"internal": [], "visible": []}

        request = self.params

        # We will need a rolling history of the chat, so we can't just append
        # the user input to the history.
        request["user_input"] = f'{current_app.config["prompt"]}\n{user_input}'
        # request["history"] = chat_history
        request[
            "chat-instruct_command"
        ] = f'{current_app.config["prompt"]}<|character|>".\n\n<|prompt|>'

        print(f"Request: {request}")

        resquest_params = {
            "json": request,
            "headers": {"ngrok-skip-browser-warning": "true"},
            "timeout": 120,
        }

        if self.basic_auth:
            resquest_params["auth"] = HTTPBasicAuth(self.username, self.password)

        response = requests.post(self.url, **resquest_params)

        print(f"Response: {response}")

        if response.status_code == 200:
            print(response.text)
            return response.json()["results"][0]["history"]["visible"][-1][1]

        return response.status_code


# https://loved-quietly-seal.ngrok-free.app


# def run(user_input, history):

#     print(response)
#     if response.status_code == 200:
#         result = response.json()['results'][0]['history']
#         print(json.dumps(result, indent=4))
#         print()
#         print(result['visible'][-1][1])


if __name__ == "__main__":
    # user_input = "Please give me a step-by-step guide on how to plant a tree in my backyard."

    # # Basic example
    # history = {'internal': [], 'visible': []}

    # # "Continue" example. Make sure to set '_continue' to True above
    # # arr = [user_input, 'Surely, here is']
    # # history = {'internal': [arr], 'visible': [arr]}

    # run(user_input, history)

    connector = OobaboogaConnector(
        base_url="https://loved-quietly-seal.ngrok-free.app",
    )

    print(connector.get_response("How to take care of a llama?"))
