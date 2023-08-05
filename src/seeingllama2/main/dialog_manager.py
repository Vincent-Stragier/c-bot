# -*- coding: utf-8 -*-
"""DialogManager class, responsible for managing the dialog system."""
from multiprocessing import Lock

from seeingllama2.main.large_language_models import connectors

# from seeingllama2.main.interpreter import interpreter

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
        api_path: str = "/api/v1/generate",
    ):
        """Initialize DialogManager."""
        MANAGER_DATA_LOCK.acquire()
        if request_id not in manager_data:
            manager_data[request_id] = {
                "request_id": request_id,
                "connector": connector,
                "base_url": base_url,
                "api_path": api_path,
                "chat_history": [],
            }

        self.request_id = request_id
        self.connector = connector
        self.base_url = base_url
        self.api_path = api_path
        self.chat_history = manager_data[request_id].get("chat_history", [])
        MANAGER_DATA_LOCK.release()

    def get_chat_history(self) -> list:
        """Get chat history."""
        MANAGER_DATA_LOCK.acquire()
        self.chat_history = list(
            manager_data[self.request_id].get("chat_history", [])
        )
        MANAGER_DATA_LOCK.release()
        return self.chat_history

    def set_chat_history(self, chat_history: list):
        """Set chat history."""
        self.chat_history = chat_history
        MANAGER_DATA_LOCK.acquire()
        manager_data[self.request_id]["chat_history"] = chat_history
        MANAGER_DATA_LOCK.release()

    def get_response(self, user_input: dict) -> list[dict]:
        """Get response from connector."""

        print(f"Text in DialogManager: {user_input['text_input']}")

        llm = connectors.GenericConnector(
            self.base_url, self.api_path, connector=self.connector
        )
        response = llm.get_response(user_input, self.chat_history)

        if response == 404:
            return [
                {
                    "error": "LLM not responding.",
                    "text": "Error: 404, LLM not responding.",
                },
            ]

        # Update chat history
        new_chat_history = self.chat_history
        new_chat_history.extend(response)
        self.chat_history = new_chat_history

        return response
