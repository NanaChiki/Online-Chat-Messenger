"""
Online Chat Messenger - Stage 1 Client
UDP-based chat server that broadcasts messages to all connected clients.
"""

import socket
import threading
import time
from typing import Dict, Tuple

try:
    from .protocol import (
        MAX_MESSAGE_SIZE,
        MSG_TYPE_CHAT,
        MSG_TYPE_DISCONNECT,
        MSG_TYPE_JOIN,
        MSG_TYPE_PING,
        decode_message,
        encode_message,
        encode_system_message,
    )
except ImportError:
    from protocol import (
        MAX_MESSAGE_SIZE,
        MSG_TYPE_CHAT,
        MSG_TYPE_DISCONNECT,
        MSG_TYPE_JOIN,
        MSG_TYPE_PING,
        decode_message,
        encode_message,
        encode_system_message,
    )


class ChatServer:
    def __init__(self, host: str = "localhost", port: int = 12345):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients: Dict[Tuple[str, int], float] = {}  # All connected clients
        self.joined_clients: Dict[
            Tuple[str, int], str
        ] = {}  # {addr: username} for joined clients
        self.running = False

    def start(self):
        """Start the UDP chat server."""
        try:
            self.sock.bind((self.host, self.port))
            self.running = True
            print(f"\n🚀 Chat Server started on {self.host}:{self.port}")
            print("👥 Waiting for clients to connect...")

            # Start client cleanup thread
            cleanup_thread = threading.Thread(target=self._cleanup_inactive_clients)
            cleanup_thread.daemon = True
            cleanup_thread.start()

            # main server loop
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(MAX_MESSAGE_SIZE)
                    self._handle_message(data, addr)
                except socket.error as e:
                    if self.running:
                        print(f"\n❌ Socket error: {e}")
                except KeyboardInterrupt:
                    print("\n👋 Server shutting down...")
                    break
        except Exception as e:
            print(f"\n❌ Sever error: {e}")
        finally:
            self.stop()

    def _handle_message(self, data: bytes, addr: tuple):
        """Handle incoming messages from clients."""
        try:
            # Update client's last_seen time
            self.clients[addr] = time.time()

            # Decode message
            username, message, msg_type = decode_message(data)
            if len(message) > MAX_MESSAGE_SIZE - 2 - len(username.encode("utf-8")):
                message_too_long = "Your message exceeds 4096 characters. Please enter a shorter message."
                self._broadcast_to_personal(
                    encode_system_message(message_too_long), addr
                )
                return

            if msg_type == MSG_TYPE_JOIN:
                self._handle_join_request(username, addr)
            elif msg_type == MSG_TYPE_CHAT:
                self._handle_chat_message(username, message, addr)
            elif msg_type == MSG_TYPE_DISCONNECT:
                self._handle_disconnect_request(username, addr)
            elif msg_type == MSG_TYPE_PING:
                self._handle_ping_request(username, addr)
            else:
                print(f"🤔 Unknown message type {msg_type} from {addr}")

        except Exception as e:
            print(f"\n❌ Error handling message from {addr}: {e}")

    def _handle_join_request(self, username: str, addr: tuple):
        """Handle client join request."""
        if addr not in self.joined_clients:
            self.joined_clients[addr] = username
            print(f"✅ {username} joined from {addr[0]}:{addr[1]}")

            # Broadcast join notification to all joined clients
            join_message = encode_system_message(f"🎉 {username} has joined the chat")
            self._broadcast_to_joined(join_message, exclude_addr=None)
        else:
            print(f"🔄 {username} already joined from {addr}")

    def _handle_chat_message(self, username: str, message: str, addr: tuple):
        """Handle regular chat message."""
        # Only allow chat from joined clients
        if addr in self.joined_clients:
            print(f"💬 [{username}] from {addr[0]}:{addr[1]}: {message}")
            # Broadcast to joined clients only
            chat_data = encode_message(username, message, MSG_TYPE_CHAT)
            self._broadcast_to_joined(chat_data, exclude_addr=addr)
        else:
            print(f"🚫 Chat message from non-joined client {addr} ignored")

    def _handle_disconnect_request(self, username: str, addr: tuple):
        """Handle explicit disconnect request from client."""
        print(
            f"🚪 {username} disconnected from {addr[0]}:{addr[1]} (explicit disconnect)"
        )
        self._handle_client_disconnect(addr, True)

    def _handle_ping_request(self, username: str, addr: tuple):
        """Handle ping request for connection testing."""
        try:
            # Respond with a simple pong message
            pong_message = encode_system_message("pong")
            self.sock.sendto(pong_message, addr)
            print(
                f"🏓 Ping from {username} at {addr[0]}:{addr[1]} - responded with pong"
            )
        except Exception as e:
            print(f"❌ Failed to respond to ping from {addr}: {e}")

    def _broadcast_to_joined(self, message_data: bytes, exclude_addr: tuple = None):
        """Broadcast a message to all joined clients."""
        disconnected_clients = []

        for client_addr in self.joined_clients.keys():
            if client_addr != exclude_addr:
                try:
                    self.sock.sendto(message_data, client_addr)
                except socket.error as e:
                    print(f"\n❌ Failed to send to {client_addr}: {e}")
                    disconnected_clients.append(client_addr)

        # Handle disconnected clients
        for addr in disconnected_clients:
            self._handle_client_disconnect(addr, False)

    def _broadcast_to_personal(self, message_data: bytes, client_addr: tuple):
        """Broadcast a message to a specific client."""
        try:
            self.sock.sendto(message_data, client_addr)
        except socket.error as e:
            print(f"\n❌ Failed to send a message to {client_addr}: {e}")

    def _handle_client_disconnect(self, addr: tuple, explicit_disconnect: bool = False):
        """Handle client disconnection with notification."""
        if addr in self.joined_clients:
            username = self.joined_clients[addr]
            del self.joined_clients[addr]

            # If the disconnect is not explicit, notify the client
            if not explicit_disconnect:
                # Notify the client has been disconnected
                print(f"🚪 {username} disconnected from {addr}")
                personal_message = "⛔️ You have been disconnected from the chat due to being inactive for too log.\n Please enter 'join' to rejoin the chat."
                encoded_personal_message = encode_system_message(personal_message)
                self._broadcast_to_personal(encoded_personal_message, addr)

            # Notify other joined clients about the disconnection
            encoded_broadcast_message = encode_system_message(
                f"👋 {username} has left the chat..."
            )
            self._broadcast_to_joined(encoded_broadcast_message, exclude_addr=None)

        # Remove from general client list too
        if addr in self.clients:
            del self.clients[addr]

    def _cleanup_inactive_clients(self):
        """Remove inactive clients periodically."""
        TIMEOUT_SECONDS = 60  # 1 minute timeout for better responsiveness

        while self.running:
            current_time = time.time()
            inactive_clients = []

            for addr, last_seen in self.clients.items():
                if current_time - last_seen > TIMEOUT_SECONDS:
                    inactive_clients.append(addr)

            # Remove inactive clients with proper disconnect handling
            for addr in inactive_clients:
                print(f"⏰ Client {addr} timed out after {TIMEOUT_SECONDS} seconds")
                self._handle_client_disconnect(addr, False)

            time.sleep(10)  # Check every 10 seconds

    def stop(self):
        """Stop the chat server."""
        print("\n✋ Stopping Chat Server...")

        # Notify all joined clients about server shutdown
        if self.joined_clients:
            shutdown_message = encode_system_message(
                "🛑 Server is shutting down. Please wait until it comes back."
            )
            self._broadcast_to_joined(shutdown_message, exclude_addr=None)
            print(f"\n📢 Notified {len(self.joined_clients)} clients about shutdown")

            # Give time for shutdown messages to be sent
            time.sleep(0.5)

        self.running = False
        if hasattr(self, "sock"):
            self.sock.close()
        print("👋 Server stopped.")


if __name__ == "__main__":
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
