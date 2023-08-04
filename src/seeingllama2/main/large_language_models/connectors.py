# -*- coding: utf-8 -*-
"""Connectors for large language models."""
from .oobabooga_connector import OobaboogaConnector

ALL_CONNECTORS = {
    "oobabooga": OobaboogaConnector,
}


class GenericConnector:
    """Generic connector class."""

    def __init__(self, base_url, api_path, connector="oobabooga"):
        """Initialize GenericConnector."""
        self.connector = ALL_CONNECTORS[connector](base_url, api_path)

    def get_response(self, input_data, chat_history):
        """Get response from connector."""
        # print(f"User input in Generic Connector: {input_data}")
        return self.connector.get_response(input_data, chat_history)

    def set_params(self, params):
        """Set parameters for connector."""
        self.connector.set_params(params)
