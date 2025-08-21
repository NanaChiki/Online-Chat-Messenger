"""
Online Chat Messenger - Stage 1 Client
UPD-based chat client for connecting to server.
"""

import socket
import threading
import sys


class ChatClient:
    def __init__(self, host: str = "localhost", port: int = 12345):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username = input("Enter your username: ")
        self.running = False

    def connect(self):
        """Connect to the chat server."""
        print(f"\n✅Connecting to Chat Server...")
        # Implementation to be added

    def disconnect(self):
        """Disconnect from the chat server."""
        print("\n✋ Disconnecting from Chat Server...")
        # Implementation to be added


if __name__ == "__main__":
    client = ChatClient()
    try:
        client.connect()
    except KeyboardInterrupt:
        client.disconnect()
