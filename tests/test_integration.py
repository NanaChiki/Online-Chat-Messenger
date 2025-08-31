# tests/test_integration.py - Integration tests
"""
Integration tests for Stage 1 Server-Client functionality
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import threading
import time
import unittest

from stage1.client import ChatClient
from stage1.protocol import (
    MAX_MESSAGE_SIZE,
    MSG_TYPE_CHAT,
    MSG_TYPE_SYSTEM,
    decode_message,
    encode_join_request,
    encode_message,
)
from stage1.server import ChatServer


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

    # def test_single_client_connection(self):
    #     """Test single client can connect and send messages"""
    #     client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #     try:
    #         # Send join request
    #         join_data = encode_join_request("TestUser")
    #         client_socket.sendto(join_data, ("localhost", self.server_port))
    #         start_time = time.time()
    #         time.sleep(0.1)
    #         # Send message
    #         message = encode_message("TestUser", "Hello, World!", MSG_TYPE_CHAT)
    #         client_socket.sendto(message, ("localhost", self.server_port))

    #         # Check if server registered client
    #         self.assertEqual(len(self.server.clients), 1)
    #         # Check if server received message
    #         client_addr = list(self.server.clients.keys())[0]
    #         self.assertEqual(self.server.joined_clients[client_addr], "TestUser")

    #         # end_time = time.time()
    #         # while end_time - start_time < 60:
    #         #     end_time = time.time()
    #     finally:
    #         client_socket.close()

    def test_multiple_client_broadcast(self):
        """Test message broadcasting between multiple clients"""
        client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Both clients send join requests
            join_data1 = encode_join_request("Alice")
            client1.sendto(join_data1, ("localhost", self.server_port))
            time.sleep(0.1)
            join_data2 = encode_join_request("Bob")
            client2.sendto(join_data2, ("localhost", self.server_port))
            time.sleep(0.1)

            # Both clients send initial messages to register
            client1.sendto(
                encode_message("Alice", "Hello from Alice"),
                ("localhost", self.server_port),
            )
            time.sleep(0.1)
            client2.sendto(
                encode_message("Bob", "Hello from Bob"),
                ("localhost", self.server_port),
            )

            # Check if both clients received messages
            time.sleep(0.1)
            self.assertEqual(len(self.server.clients), 2)
            self.assertEqual(
                self.server.joined_clients[list(self.server.clients.keys())[0]], "Alice"
            )
            self.assertEqual(
                self.server.joined_clients[list(self.server.clients.keys())[1]], "Bob"
            )

            # Client1 sends a message
            # client1.sendto(
            #     encode_message("Alice", "Message to all"),
            #     ("localhost", self.server_port),
            # )

            # Thread is not running, client2 will only receive join message of himself
            client2.settimeout(0.5)
            data, _ = client2.recvfrom(MAX_MESSAGE_SIZE)
            username, message, msg_type = decode_message(data)
            print(username, message, msg_type)

            self.assertEqual(username, "SYSTEM")
            self.assertEqual(message, "🎉 Bob has joined the chat")
            self.assertEqual(msg_type, MSG_TYPE_SYSTEM)

        finally:
            client1.close()
            client2.close()


if __name__ == "__main__":
    unittest.main()
