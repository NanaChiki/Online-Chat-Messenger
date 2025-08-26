# tests/test_integration.py - Integration tests
"""
Integration tests for Stage 1 Server-Client functionality
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import socket
import threading
import time
from stage1.server import ChatServer
from stage1.protocol import (
    encode_message,
    decode_message,
    MAX_MESSAGE_SIZE,
)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test server and clients"""
        self.server_port = 12344  # Use different port to avoid conflicts
        self.server = ChatServer("localhost", self.server_port)

        # Start server in background thread
        self.server_thread = threading.Thread(target=self.server.start)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.1)  # Give server time to start

    def tearDown(self):
        """Clean up after tests"""
        self.server.stop()
        time.sleep(0.1)

    def test_single_client_connection(self):
        """Test single client can connect and send messages"""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Send message
            message = encode_message("TestUser", "Hello, World!")
            client_socket.sendto(message, ("localhost", self.server_port))

            # Check if server registered client
            time.sleep(0.1)
            self.assertEqual(len(self.server.clients), 1)
        finally:
            client_socket.close()

    def test_multiple_client_broadcast(self):
        """Test message broadcasting between multiple clients"""
        client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Both clients send initial messages to register
            client1.sendto(
                encode_message("Alice", "Hello from Alice"),
                ("localhost", self.server_port),
            )
            client2.sendto(
                encode_message("Bob", "Hello from Bob"),
                ("localhost", self.server_port),
            )

            # Check if both clients received messages
            time.sleep(0.1)
            self.assertEqual(len(self.server.clients), 2)

            # Client1 sends a message
            client1.sendto(
                encode_message("Alice", "Message to all"),
                ("localhost", self.server_port),
            )

            # Client2 should receive it
            client2.settimeout(0.1)
            data, _ = client2.recvfrom(MAX_MESSAGE_SIZE)
            username, message = decode_message(data)

            # Check if client2 received the message
            self.assertEqual(username, "Alice")
            self.assertEqual(message, "Message to all")

        finally:
            client1.close()
            client2.close()


if __name__ == "__main__":
    unittest.main()
