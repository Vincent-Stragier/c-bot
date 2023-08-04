# -*- coding: utf-8 -*-
"""OobaboogaConnector class."""
from datetime import datetime

import requests
from flask import current_app
from requests.auth import HTTPBasicAuth

REQUEST_TIMEOUT = 120

DEFAULT_PARAMS = {
    "prompt": "",
    "max_new_tokens": 512,
    "temperature": 0.1,
    "top_p": 0.6,
    # "repetition_penalty": 0.1,
    "top_k": 40,
    "stopping_strings": ["</bot>", "</end>", "[INST]", "[Inst]"],
}


class OobaboogaConnector:
    """Class for connecting to OobaBooga."""

    def __init__(
        self, base_url="http://127.0.0.1:7860", api_path="/api/v1/chat"
    ):
        """Initialize OobaBoogaConnector."""
        self.url = base_url + api_path
        self.params = DEFAULT_PARAMS
        self.basic_auth = False

        if current_app.config["config"]["llm_api"].get(
            "http_basic_auth", False
        ):
            self.basic_auth = True
            self.username = current_app.config["config"]["llm_api"][
                "http_basic_auth"
            ]["username"]
            self.password = current_app.config["config"]["llm_api"][
                "http_basic_auth"
            ]["password"]

    def decorate_history(self, history: list) -> str:
        """Decorate the history.

        Args:
            history (list): The history.

        Returns:
            str: The decorated history.
        """
        decorated_history = ""

        for entry in history:
            match entry["origin"]:
                case "user":
                    decorated_history += f"<user>{entry['text']}</user>\n"
                case "tool":
                    decorated_history += f"<tool>{entry['text']}</tool>\n"
                case "bot":
                    decorated_history += (
                        f"[/INST]<bot to={entry['destination']}>"
                        f"{entry['text']}</bot>[INST]\n"
                    )
                case _:
                    raise ValueError(f"Invalid origin: {entry['origin']}")

        return decorated_history

    def api_request(self, request: dict) -> requests.Response:
        """Send a request to OobaBooga.

        Args:
            request (dict): the request.

        Returns:
            requests.Response: the response.
        """

        request_params = {
            "json": request,
            "headers": {"ngrok-skip-browser-warning": "true"},
            "timeout": REQUEST_TIMEOUT,
        }

        if self.basic_auth:
            request_params["auth"] = HTTPBasicAuth(
                self.username, self.password
            )

        return requests.post(self.url, **request_params)

    def generate(
        self,
        entity_input: str,
        origin: str = "user",
        destination: str | None = None,
        ghosting_prompt: str = "",
        history: list | None = None,
        max_new_tokens: int = 200,
    ) -> list:
        """Generate text from the model.

        Args:
            entity_input (str): The user or tool input.
            origin (str, optional): The destination (user or tool).
            Defaults to "user".
            prompt (str, optional): The prompt. Defaults to "".
            history (list, optional): The history. Defaults to None.
            max_new_tokens (int, optional): The maximum number of tokens to
            generate. Defaults to 200.

        Returns:
            list: Last entry of the history and the response from the API.

        Raises:
            ValueError: If the origin is invalid.

            # For Look for a person, ...
            "temperature": 0.1,
            "top_p": 0.6,
            # "repetition_penalty": 1.18,
            "top_k": 40,
        """
        if destination is None:
            destination = "bot"

        entity_input_dict = {
            "text": entity_input,
            "origin": origin,
            "destination": destination,
            "date": f"{datetime.now()}",
        }

        if history is None:
            history = [entity_input_dict]

        else:
            # Make a copy of the history so we don't modify the original
            history = history.copy()
            history.append(entity_input_dict)

        new_prompt = ghosting_prompt

        match origin:
            case "user":
                new_prompt += self.decorate_history(history[-3:])
                new_prompt += '\n[/INST]<bot to="tool">'

            case "tool":
                new_prompt += self.decorate_history(history[-5:])
                new_prompt += '\n[/INST]<bot to="user">'

            case _:
                raise ValueError(f"Invalid origin: {origin}")

        request = self.params.copy()
        request["prompt"] = new_prompt
        request["max_new_tokens"] = max_new_tokens

        request_response = self.api_request(request)

        if request_response.status_code == 200:
            return [
                history[-1],
                {
                    "text": request_response.json()["results"][0]["text"],
                    "origin": "bot",
                    "destination": "tool" if origin == "user" else "user",
                    "date": f"{datetime.now()}",
                },
            ]

        return [history[-1], {}]

    def set_params(self, params: dict):
        """Set the parameters.

        Args:
            params (dict): the parameters.
        """
        self.params = params

    # def get_response(
    #     self, user_input: str, chat_history: dict | None = None):
    #     """Send a request to OobaBooga.

    #     Args:
    #         user_input (str): the user input.
    #         history (dict, optional): the history. Defaults to None.

    #     Returns:
    #         requests.Response: the response.
    #     """

    #     if chat_history is None:
    #         chat_history = {"internal": [], "visible": []}

    #     request = self.params

    #     # We will need a rolling history of the chat, so we can't just append
    #     # the user input to the history.
    #     request[
    #         "user_input"
    #     ] = f'{current_app.config["prompt"]}\n{user_input}'
    #     # request["history"] = chat_history
    #     request[
    #         "chat-instruct_command"
    #     ] = f'{current_app.config["prompt"]}<|character|>".\n\n<|prompt|>'
    #     request["your_name"] = current_app.config["config"]["js_app"].get(
    #         "username", "You"),

    #     print(f"Request: {request}")

    #     resquest_params = {
    #         "json": request,
    #         "headers": {"ngrok-skip-browser-warning": "true"},
    #         "timeout": 120,
    #     }

    #     if self.basic_auth:
    #         resquest_params["auth"] = HTTPBasicAuth(
    #             self.username, self.password)

    #     response = requests.post(self.url, **resquest_params)

    #     print(f"Response: {response}")

    #     if response.status_code == 200:
    #         print(response.text)
    #         return response.json()["results"][0]["history"]["visible"][-1][1]

    #     return response.status_code


# def model_api(request: dict):
#     """Interact with the model parameters.

#     Args:
#         request (dict): _description_

#     Returns:
#         _type_: _description_
#     """
#     response = requests.post(
#         f"{HOST}/api/v1/model", json=request, auth=AUTH,
#         timeout=REQUEST_TIMEOUT
#     )
#     return response.json()


# if __name__ == "__main__":
# [INST] <<SYS>>
# You are a helpful, respectful and honest assistant.
# Always answer as helpfully as possible, while being safe.
# Your answers should not include any harmful, unethical, racist, sexist,
# toxic, dangerous, or illegal content. Please ensure that
# your responses are socially unbiased and positive in nature.
# If a question does not make any sense, or is not factually coherent,
# explain why instead of answering something not correct.
# If you don't know the answer to a question,
# please don't share false information.
# <</SYS>>
# {prompt} [/INST] {model_reply} [INST] {prompt} [/INST]

# with open("prompt.txt", "r", encoding="utf-8") as prompt_file:
#     prompt = prompt_file.read()

# chat_history = [
#     {
#         "text": "Where am I?",
#         "origin": "user",
#         "destination": "bot",
#         "date": "",
#     },
#     {
#         "text": "position()",
#         "origin": "bot",
#         "destination": "tool",
#         "date": "",
#     },
#     {
#         "text": "Sesame Street, New York City, New York, USA",
#         "origin": "tool",
#         "destination": "bot",
#         "date": "",
#     },
#     {
#         "text": "You are in Sesame Street, New York City, New York, USA",
#         "origin": "bot",
#         "destination": "user",
#         "date": "",
#     },
# ]

# # print(decorate_history(chat_history))

# user_input = "Is Yann LeCun here?"

# # user_input = "Is there a chair in front of me?"
# # user_input = "Could you help me locate a chair nearby?"
# # user_input = f'{prompt}<user>{user_input}</user>[/INST]\n<bot to="tool">'
# bot_to_tool = generate(
#     user_input, ghosting_prompt=prompt,
#     history=chat_history, max_new_tokens=512
# )

# chat_history.extend(bot_to_tool)

# tool_input = "True"

# bot_to_user = generate(
#     tool_input,
#     ghosting_prompt=prompt,
#     origin="tool",
#     history=chat_history,
#     max_new_tokens=512,
# )

# chat_history.extend(bot_to_user)

# print(decorate_history(chat_history))
