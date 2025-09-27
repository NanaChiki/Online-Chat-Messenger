#!/usr/bin/env python3
"""
UDP Server for Stage 2 Chat Room Messaging
Handles real-time chat within rooms created via TCP
"""

import socket
import threading
import time
from typing import Dict, Optional, Set

from room_manager import Room
from tcp_protocol import TokenManager
from udp_protocol import (
    MSG_TYPE_CHAT,
    MSG_TYPE_SYSTEM,
    MSG_TYPE_USER_JOIN,
    MSG_TYPE_USER_LEAVE,
    decode_udp_message,
    encode_server_message,
    encode_udp_message,
)


class UDPChatServer:
    """UDP server for room-based chat messaging"""

    def __init__(self, host: str = "localhost", port: int = 12347):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Shared state (will be injected unified server)
        self.rooms: Dict[str, Room] = {}
        self.token_manager = TokenManager()

        # New: Client address tracking for UDP broadcasting
        self.client_addresses: Dict[str, tuple] = {}  # {token: (ip, port)}
        self.running = False

        print(f"\n🟢 UDP Chat Server initialized on {self.host}:{self.port}")

    def start(self):
        """Start the UDP server"""
        try:
            self.sock.bind((self.host, self.port))
            self.running = True
            print(f"🚀 UDP Chat Server listening on {self.host}:{self.port}")

            while self.running:
                try:
                    data, client_addr = self.sock.recvfrom(4096)

                    # Process each message in a separate thread
                    threading.Thread(
                        target=self._handle_message,
                        args=(data, client_addr),
                        daemon=True,
                    ).start()
                except socket.error as e:
                    if self.running:
                        print(f"🔴 UDP socket error: {e}")
        except Exception as e:
            print(f"🔴 UDP server error: {e}")
        finally:
            self.stop()

    def set_shared_state(self, rooms: Dict[str, Room], token_manager: TokenManager):
        """Inject shared state from TCP server"""
        self.rooms = rooms
        self.token_manager = token_manager
        print("\n🔗 UDP server linked to TCP server state (shared state)")

    def _handle_message(self, data: bytes, client_addr: tuple):
        """Process a single UDP message"""
        try:
            # Decode the UDP message
            udp_msg = decode_udp_message(data)
            print(
                f"\n📨 UDP message from {client_addr}: room='{udp_msg.room_name}' msg='{udp_msg.message[:50]}...'"
            )

            # Validate token and get user info
            user_info = self._validate_client(
                udp_msg.token, udp_msg.room_name, client_addr[0]
            )
            if not user_info:
                return  # Invalid client, ignore message

            username = user_info["username"]

            # New: Update client address mapping for broadcasting
            self._update_client_address(udp_msg.token, client_addr)

            # Broadcast message to all room participants
            self._broadcast_to_room(
                udp_msg.room_name, MSG_TYPE_CHAT, username, udp_msg.message
            )

        except Exception as e:
            print(f"🔴 Error handling UDP message from {client_addr}: {e}")

    def _update_client_address(self, token: str, client_addr: tuple):
        """
        Update client address mapping for broadcasting

        Args:
            token: client's authentication token
            client_addr: (ip, port) tuple from UDP packet
        """
        previous_addr = self.client_addresses.get(token)
        self.client_addresses[token] = client_addr

        if previous_addr != client_addr:
            print(
                f"🔄 Updated address for token {token[:8]}...: {previous_addr} -> {client_addr}"
            )

    def _broadcast_to_room(
        self, room_name: str, msg_type: int, sender_username: str, message: str
    ):
        """
        Broadcast message to all participants in the room

        Error Specifications:
        - Room not found: Skip broadcast if room no longer exists
        - Socket errors: Log failed sends but continue with others
        - Encoding errors: Skip malformed messages
        """
        try:
            if room_name not in self.rooms:
                print(f"❌ Cannot broadcast: room '{room_name}' not found")
                return

            room = self.rooms[room_name]
            participant_count = len(room.participants)

            if participant_count == 0:
                print(f"📭 No participants in room '{room_name}' to broadcast to")
                return

            # Create server message
            server_msg = encode_server_message(msg_type, sender_username, message)
            successful_sends = 0

            # Send to all room participants who have known UDP addresses
            for token, participant in room.participants.items():
                try:
                    # Check if we have this client's UDP address
                    if token not in self.client_addresses:
                        print(
                            f"⚠️ No UDP address known for {participant['username']} (token {token[:8]}...)"
                        )
                        continue

                    client_addr = self.client_addresses[token]

                    # Send UDP message to client
                    self.sock.sendto(server_msg, client_addr)
                    print(
                        f"\n📤 Broadcasting to {participant['username']} at {client_addr}"
                    )
                    successful_sends += 1

                except Exception as send_error:
                    print(
                        f"❌ Failed to send to {participant.get('username', 'unknown')}: {send_error}"
                    )

            print(
                f"\n📡 Broadcast complete: {successful_sends}/{participant_count} delivered to room '{room_name}'"
            )
        except Exception as e:
            print(f"🔴 Broadcast error for room '{room_name}': {e}")

    def _validate_client(
        self, token: str, room_name: str, client_ip: str
    ) -> Optional[Dict]:
        """
        Validate client token, room access, and IP binding

        Returns user info dict if valid, None if invalid
        Error Specifications:
        - Invalid token: Token not found or expired
        - Room not found: Requested room does not exist or expired
        - IP mismatch: Client IP does not match token registration
        - Not room participant: User not in the requested room
        """
        try:
            # 1. Validate token exists and is active
            if not self.token_manager or not self.token_manager.validate_token(
                token, client_ip
            ):
                print(f"❌ Invalid token: {token[:8]}... from {client_ip} ")
                return None

            # 2. Check if room exists
            if room_name not in self.rooms:
                print(f"❌ Room '{room_name}' not found for token {token[:8]}...")
                return None

            room = self.rooms[room_name]

            # 3. Verify user is a participant in this room
            if token not in room.participants:
                print(f"❌ Token {token[:8]}... not authorized for room '{room_name}'")
                return None

            user_info = room.participants[token]

            # 4. Validate IP address binding (security requirement)
            if user_info["ip"] != client_ip:
                print(
                    f"❌ IP mismatch for token {token[:8]}...: expected {user_info['ip']} but got {client_ip}"
                )
                return None

            print(f"\n✅ Validated user {user_info['username']} in room '{room_name}'")
            return user_info

        except Exception as e:
            print(f"❌ Validation error: {e}")
            return None

    def stop(self):
        """Stop the UDP server"""
        self.running = False
        if self.sock:
            self.sock.close()
        print("\n🛑 UDP Chat Server stopped")


if __name__ == "__main__":
    # Basic testing
    server = UDPChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n👋 shutting down UDP server...")
        server.stop()
