# -*- coding: utf-8 -*-
"""This module contains the DialogManager class, which is responsible for managing the dialog system."""
from multiprocessing import Lock

from flask import current_app

from seeingllama2.main.large_language_models import connectors
from seeingllama2.main.interpreter import interpreter

MANAGER_DATA_LOCK = Lock()


# manager_data = {
#     # Request ID: ...
#     "1230": {
#         "request_id": "1230",
#         "connector": "oobabooga",
#         "base_url": "http://localhost:5000",
#         "api_path": "/api/v1",
#         "chat_history": {"internal": [], "visible": []},
#     }
# }
manager_data = {}


class DialogManager:
    """Dialog manager class."""

    def __init__(
        self,
        request_id: str,
        connector: str = "oobabooga",
        base_url: str = "http://localhost:5000",
        api_path: str = "/api/v1",
    ):
        """Initialize DialogManager."""
        MANAGER_DATA_LOCK.acquire()

        if request_id not in manager_data:
            manager_data[request_id] = {
                "request_id": request_id,
                "connector": connector,
                "base_url": base_url,
                "api_path": api_path,
                "chat_history": {"internal": [], "visible": []},
            }

        self.request_id = request_id
        self.connector = connector
        self.base_url = base_url
        self.api_path = api_path
        self.chat_history = manager_data[request_id]["chat_history"]
        MANAGER_DATA_LOCK.release()

    def get_chat_history(self):
        """Get chat history."""
        MANAGER_DATA_LOCK.acquire()
        self.chat_history = manager_data[self.request_id]["chat_history"]
        MANAGER_DATA_LOCK.release()
        return self.chat_history

    def set_chat_history(self, chat_history: dict):
        """Set chat history."""
        self.chat_history = chat_history
        MANAGER_DATA_LOCK.acquire()
        manager_data[self.request_id]["chat_history"] = chat_history
        MANAGER_DATA_LOCK.release()

    def get_response(self, user_input: str):
        """Get response from connector."""
        # Receive user input
        # Send user input to LLM

        print(f"User input in DM: {user_input}")
        llm = connectors.GenericConnector(
            self.base_url, self.api_path, connector=self.connector
        )
        response = llm.get_response(user_input, self.chat_history)

        print(f"Response from LLM: {response}")

        if response == 404:
            return "Error: LLM not responding."

        # Update chat history
        self.chat_history["visible"].append(["user", user_input])
        self.chat_history["visible"].append(["llm", response])

        print(self.chat_history)

        # Parse response from LLM <bot to='tool'>function(param1, param2)</bot>
        tool_call = str(response)
        tool_call = tool_call[tool_call.rfind("<bot to=") + 10 :]

        tool_response = interpreter(tool_call, run=True)

        print(f"Tool response: {tool_response}")

        # Run corresponding tool

        return response

        # Receive response from LLM
        # Interpret response from LLM and activate appropriate modules
        # Send the modules' responses to the LLM
        # Receive response from LLM
        # Send response to user

    # def state_machine()
