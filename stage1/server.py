"""
Online Chat Messenger - Stage 1 Client
UDP-based chat server that broadcasts messages to all connected clients.
"""

import socket
import threading
import time
from typing import Dict, Set, Tuple


class ChatServer:
    def __init__(self, host: str = "localhost", port: int = 12345):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients: Dict[Tuple[str, int], float] = {}
        self.running = False

    def start(self):
        """Start the UDP chat server."""
        print(f"Starting Chat Server on {self.host}:{self.port}")
        # Implementation to be added

    def stop(self):
        """Stop the chat server."""
        print("✋ Stopping Chat Server...")
        # Implementation to be added


if __name__ == "__main__":
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
