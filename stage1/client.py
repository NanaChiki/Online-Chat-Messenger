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
        MSG_TYPE_PING,
        MSG_TYPE_SYSTEM,
        decode_message,
        encode_disconnect_request,
        encode_join_request,
        encode_message,
        encode_ping_request,
    )
except ImportError:
    from protocol import (
        MAX_MESSAGE_SIZE,
        MSG_TYPE_CHAT,
        MSG_TYPE_DISCONNECT,
        MSG_TYPE_PING,
        MSG_TYPE_SYSTEM,
        decode_message,
        encode_disconnect_request,
        encode_join_request,
        encode_message,
        encode_ping_request,
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
            # 1. A warning message won't be shown if connection happens when the server is not running
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
                data, _ = self.sock.recvfrom(MAX_MESSAGE_SIZE)
                username, message, msg_type = decode_message(data)
                if (
                    message
                    == "🛑 Server is shutting down. Please wait until it comes back."
                ):
                    raise Exception(message)

                # Clear current input line if prompt was shown
                if self.prompt_shown:
                    self._clear_input_line()

                if msg_type == MSG_TYPE_SYSTEM:
                    # Display system notifications
                    print(f"🔔 {message}")
                    if (
                        message
                        == "⛔️ You have been disconnected from the chat due to being inactive for too log.\n Please enter 'join' to rejoin the chat."
                    ):
                        self.joined = False

                elif msg_type == MSG_TYPE_CHAT and username != self.username:
                    # Display chat messages from others
                    print(f"💬 [{username}]: {message}")

                # Restore input prompt
                self._show_prompt()

            except socket.error:
                if self.running:
                    self._handle_connection_lost()

            except Exception as e:
                if self.running:
                    print(f"\n❌ Error receiving messages: {e}")
                    self._handle_connection_lost()

    def _handle_connection_lost(self):
        """Handle connection lost to server."""
        print("\n🔌 Connection lost. Trying to reconnect...")
        self.joined = False  # Need to rejoin when server comes back

        # Close current socket
        try:
            self.sock.close()
        except:
            pass

        # Try to reconnect periodically
        reconnect_attempts = 0
        while self.running:
            try:
                reconnect_attempts += 1

                # Create fresh socket with timeout
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.settimeout(3)  # 3 second timeout for ping test

                # Send ping to test server availability
                ping_data = encode_ping_request(self.username)
                self.sock.sendto(ping_data, (self.host, self.port))

                # Wait for pong response
                try:
                    data, _ = self.sock.recvfrom(MAX_MESSAGE_SIZE)
                    _, message, msg_type = decode_message(data)

                    # If we get a pong response, server is back
                    if msg_type == MSG_TYPE_SYSTEM and message == "pong":
                        self.sock.settimeout(
                            None
                        )  # Remove timeout for normal operation
                        print(
                            "\n✅ Connection restored! Please type 'join' to re-enter chat."
                        )
                        time.sleep(0.5)
                        # Restore the prompt since main thread is still in input()
                        self._show_prompt()
                        break

                except socket.timeout:
                    # Server didn't respond to ping
                    pass
                except Exception:
                    # Any other error means server might not be ready
                    pass

            except Exception:
                pass  # Connection failed, will retry

            if reconnect_attempts % 6 == 0:  # Show message every 30 seconds
                print(f"⏳ Still trying to reconnect... (attempt {reconnect_attempts})")
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
