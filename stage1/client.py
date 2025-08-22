"""
Online Chat Messenger - Stage 1 Client
UPD-based chat client for connecting to server.
"""

import socket
import threading
import sys
from protocol import encode_message, decode_message, MAX_MESSAGE_SIZE


class ChatClient:
    def __init__(self, host: str = "localhost", port: int = 12345):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username = input("Enter your username: ")
        self.running = False

    def connect(self):
        """Connect to the chat server."""
        print(f"\n🔌 Connecting to {self.host}:{self.port}")
        print(f"👤 Username: {self.username}")
        print("Type messages and press Enter. Ctrl+C to quit.\n")

        self.running = True

        # Start message receiving thread
        receive_thread = threading.Thread(target=self._receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Main client loop
        try:
            while self.running:
                message = input("💬 ")
                if message.lower() == "quit":
                    self.disconnect()
                    break
                if message.strip():
                    self._send_message(message)
        except EOFError:
            pass

    def _send_message(self, message: str):
        """Send a message to the server."""
        # Implementation to be added
        try:
            # 1. Encode message using protocol
            encoded_message = encode_message(self.username, message=message)
            # 2. Send via UDP socket
            self.sock.sendto(encoded_message, (self.host, self.port))

        except Exception as e:
            print(f"\n❌ Failed to send message: {e}")

    def _receive_messages(self):
        """Receive and display messages from server."""
        # Implementation to be added
        while self.running:
            try:
                # 1. Listen for incoming messages
                data, addr = self.sock.recvfrom(MAX_MESSAGE_SIZE)
                # 2. Decode and display them
                username, message = decode_message(data)
                print(f"[{username}]:{message}")

                # Don't display our own messages
                if username != self.username:
                    print(f"\n💬[{username}]:{message}")
                    print("💬", end="", flush=True)  # Reprint

            except socket.error as e:
                if self.running:
                    print(f"\n❌ Connection to server lost: {e}")
                    break

            except Exception as e:
                if self.running:
                    print(f"\n❌ Error receiving messages: {e}")

    def disconnect(self):
        """Disconnect from the chat server."""
        print("\n✋ Disconnecting from Chat Server...")
        self.running = False
        self.sock.close()
        print("\n👋 Disconnected from Chat Server")


if __name__ == "__main__":
    client = ChatClient()
    try:
        client.connect()
    except KeyboardInterrupt:
        client.disconnect()
