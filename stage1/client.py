"""
Online Chat Messenger - Stage 1 Client
UPD-based chat client for connecting to server.
"""

import socket
import threading
import time

try:
    from .protocol import (
        MAX_MESSAGE_SIZE,
        MSG_TYPE_CHAT,
        MSG_TYPE_DISCONNECT,
        MSG_TYPE_SYSTEM,
        decode_message,
        encode_disconnect_request,
        encode_join_request,
        encode_message,
    )
except ImportError:
    from protocol import (
        MAX_MESSAGE_SIZE,
        MSG_TYPE_CHAT,
        MSG_TYPE_DISCONNECT,
        MSG_TYPE_SYSTEM,
        decode_message,
        encode_disconnect_request,
        encode_join_request,
        encode_message,
    )


class ChatClient:
    def __init__(self, host: str = "localhost", port: int = 12345):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username = input("Enter your username: ")
        self.running = False
        self.joined = False
        self.prompt_shown = False

    def connect(self):
        """Connect to the chat server."""
        print(f"\n🔌 Connecting to {self.host}:{self.port}")
        print(f"👤 Username: {self.username}")
        print(
            "💡 Type 'join' to enter the chat, then send messages. Type 'quit' to exit.\n"
        )

        self.running = True

        # Start message receiving thread
        receive_thread = threading.Thread(target=self._receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Show initial prompt
        self._show_prompt()

        # Main client loop
        try:
            while self.running:
                message = input()

                if message.lower() == "quit":
                    self._send_disconnect_if_joined()
                    self.disconnect()
                    break

                if message.strip():
                    if message.lower() == "join" and not self.joined:
                        self._send_join_request()
                    elif self.joined:
                        self._send_message(message)
                    else:
                        self._show_not_joined_message()

                # Show prompt for next input
                if self.running:
                    self._show_prompt()

        except (EOFError, KeyboardInterrupt):
            self._send_disconnect_if_joined()
            self.disconnect()

    def _send_join_request(self):
        """Send join request to server."""
        try:
            join_data = encode_join_request(self.username)
            self.sock.sendto(join_data, (self.host, self.port))
            self.joined = True
            print("📡 Join request sent! You can now send messages.")
        except Exception as e:
            print(f"❌ Failed to join: {e}")

    def _show_not_joined_message(self):
        """Show message when user tries to chat without joining."""
        print("⚠️  Please type 'join' first to enter the chat!")

    def _send_disconnect_if_joined(self):
        """Send disconnect message to server if currently joined."""
        if self.joined and self.running:
            try:
                disconnect_data = encode_disconnect_request(self.username)
                self.sock.sendto(disconnect_data, (self.host, self.port))
                print("📤 Disconnect notification sent to server")
                time.sleep(0.1)  # Give a moment for message to be sent
            except Exception as e:
                print(f"⚠️  Failed to send disconnect notification: {e}")

    def _show_prompt(self):
        """Show the input prompt."""
        print("🗣️ ", end="", flush=True)
        self.prompt_shown = True

    def _send_message(self, message: str):
        """Send a chat message to the server."""
        try:
            encoded_message = encode_message(self.username, message, MSG_TYPE_CHAT)
            self.sock.sendto(encoded_message, (self.host, self.port))
        except Exception as e:
            print(f"\n❌ Failed to send message: {e}")
            if self.running:
                self._show_prompt()

    def _receive_messages(self):
        """Receive and display messages from server."""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(MAX_MESSAGE_SIZE)
                username, message, msg_type = decode_message(data)

                # Clear current input line if prompt was shown
                if self.prompt_shown:
                    self._clear_input_line()

                if msg_type == MSG_TYPE_SYSTEM:
                    # Display system notifications
                    print(f"🔔 {message}")
                elif msg_type == MSG_TYPE_CHAT and username != self.username:
                    # Display chat messages from others
                    print(f"💬 [{username}]: {message}")

                # Restore input prompt
                self._show_prompt()

            except socket.error:
                if self.running:
                    self._handle_connection_lost()
                    break
            except Exception as e:
                if self.running:
                    print(f"\n❌ Error receiving messages: {e}")

    def _handle_connection_lost(self):
        """Handle connection lost to server."""
        print("\n🔌 Connection lost. Trying to reconnect...")
        self.joined = False  # Need to rejoin when server comes back

        # Try to reconnect periodically
        while self.running:
            try:
                # Test connection with a heartbeat
                test_data = encode_message(self.username, "heartbeat", 3)
                self.sock.sendto(test_data, (self.host, self.port))
                print("✅ Connection restored! Please type 'join' to re-enter chat.")
                break
            except Exception:
                time.sleep(5)  # Wait 5 seconds before retry

    def _clear_input_line(self):
        """Clear the current input line in terminal."""
        # Move cursor to beginning of line and clear it
        print("\r" + " " * 80 + "\r", end="", flush=True)
        self.prompt_shown = False

    def disconnect(self):
        """Disconnect from the chat server."""
        print("\n✋ Disconnecting from Chat Server")
        self.running = False
        self.sock.close()
        print("\n👋 Disconnected from Chat Server")


if __name__ == "__main__":
    client = ChatClient()
    try:
        client.connect()
    except KeyboardInterrupt:
        client.disconnect()
