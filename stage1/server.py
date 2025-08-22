"""
Online Chat Messenger - Stage 1 Client
UDP-based chat server that broadcasts messages to all connected clients.
"""

import socket
import threading
import time
from typing import Dict, Set, Tuple
from protocol import encode_message, decode_message, MAX_MESSAGE_SIZE


class ChatServer:
    def __init__(self, host: str = "localhost", port: int = 12345):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients: Dict[Tuple[str, int], float] = {}
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
        # Implementation needed:
        try:
            # 1. Update client's last_seen time
            self.clients[addr] = time.time()
            # 2. Decode message
            username, message = decode_message(data)
            # 2.1 Print server log
            print(f"📨[{username}] from {addr[0]}:{addr[1]}: {message}")

            # 3. Broadcast to all active clients
            self._broadcast_message(data, addr)

        except Exception as e:
            print(f"\n❌ Error handling message from {addr}: {e}")

    def _broadcast_message(self, message_data: bytes, sender_addr: tuple):
        """Broadcast a message to all connected clients except sender."""
        disconnected_clients = []

        for client_addr in self.clients.keys():
            if client_addr != sender_addr:  # dont send back to sender
                try:
                    self.sock.sendto(message_data, client_addr)
                except socket.error as e:
                    print(f"\n❌ Failed to send to {client_addr}: {e}")
                    disconnected_clients.append(client_addr)
        # Remove disconnected clients
        for addr in disconnected_clients:
            del self.clients[addr]
            print(f"🚪 Client {addr} removed due to send failure")

    def _cleanup_inactive_clients(self):
        """Remove inactive clients periodically."""
        TIMEOUT_SECONDS = 300  # 5 minutes timeout

        while self.running:
            current_time = time.time()
            inactive_clients = []

            for addr, last_seen in self.clients.items():
                if current_time - last_seen > TIMEOUT_SECONDS:
                    inactive_clients.append(addr)

            # Remove inactive clients
            for addr in inactive_clients:
                del self.clients[addr]
                print(
                    f"⏰ Client {addr} timed out and removed after {TIMEOUT_SECONDS} seconds of inactivity"
                )

            time.sleep(10)  # Check every 10 seconds

    def stop(self):
        """Stop the chat server."""
        print("\n✋ Stopping Chat Server...")
        self.running = False
        self.sock.close()
        print("👋 Server stopped.")


if __name__ == "__main__":
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
