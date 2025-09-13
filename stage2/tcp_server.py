#!/usr/bin/env python3
"""
TCP Server for Stage 2 Chat Room Management
Handles room creation and joining via TCRP protocol
"""

import socket
import threading
import time
from typing import Dict, Optional, Tuple

from room_manager import Room
from tcp_protocol import (
    TCRPMessage,
    TCRPOperation,
    TCRPState,
    TCRPStatusCodes,
    TokenManager,
    create_room_complete,
    create_room_response,
    decode_tcrp_message,
    encode_tcrp_message,
    join_room_complete,
    join_room_request,
    join_room_response,
    validate_room_name,
    validate_username,
)


class TCRPServer:
    """TCP server for chat room management using TCRP protocol"""

    def __init__(self, host: str = "localhost", port: int = 12346):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Core components
        self.rooms = {}  # {room_name: {host: username, clients: {username: client_ip}}}
        self.token_manager = TokenManager()
        self.running = False

    def start(self):
        """Start the TCP server"""
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            self.running = True
            print(f"🚀 TCP Room Server started on {self.host}:{self.port}")
            print("\n👥 Ready to handle room creation and joining requests...")

            while self.running:
                try:
                    client_sock, client_addr = self.sock.accept()
                    print(f"\n🔗 New client connected: {client_addr}")

                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_sock, client_addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except Exception as e:
                    if self.running:
                        print(f"\n❌ Socket error: {e}")
                except KeyboardInterrupt:
                    print("\n👋 Server shutting down...")
                    break
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.stop()

    def handle_client(self, client_sock: socket.socket, client_addr: tuple):
        """Handle individual client TCRP transactions"""
        try:
            # Receive TCRP message
            data = client_sock.recv(4096)  # Adjust size as needed
            if not data:
                return

            # Decode TCRP message
            message = decode_tcrp_message(data)
            print(
                f"\n📨 Received {message.operation.name} request for room '{message.room_name}'"
            )

            # Route to appropriate handler based on operation
            if message.operation == TCRPOperation.CREATE_ROOM:
                self.handle_create_room(client_sock, client_addr, message)
            elif message.operation == TCRPOperation.JOIN_ROOM:
                self.handle_join_room(client_sock, client_addr, message)
            else:
                print(f"\n❓ Unknown operation: {message.operation.name}")
        except Exception as e:
            print(f"\n❌ Error handling client {client_addr}: {e}")
        finally:
            client_sock.close()

    def handle_create_room(
        self, client_sock: socket.socket, client_addr: tuple, message: TCRPMessage
    ):
        """Handle room creation request"""
        try:
            # Extract request data
            username = message.payload["username"]
            password = message.payload["password"]
            room_name = message.room_name
            client_ip = client_addr[0]

            # RESPONSE phase
            result, result_message = self.create_room(
                room_name, username, client_ip, password
            )

            if result:
                response = create_room_response(
                    room_name, TCRPStatusCodes.SUCCESS, result_message
                )
            else:
                # Determine appropriate status code
                if "already exists" in result_message:
                    status_code = TCRPStatusCodes.ROOM_EXISTS
                elif "Invalid" in result_message:
                    status_code = (
                        TCRPStatusCodes.INVALID_USERNAME
                        if "username" in result_message
                        else TCRPStatusCodes.INVALID_NAME
                    )
                else:
                    status_code = TCRPStatusCodes.SERVER_ERROR

                response = create_room_response(room_name, status_code, result_message)

            # Send response
            client_sock.send(encode_tcrp_message(response))

            # COMPLETION phase (only if successful)
            if result:
                # Generate token for host
                token = self.token_manager.create_token(room_name, username, client_ip)

                # Add host to room
                room = self.rooms[room_name]
                room.add_participant(token, username, client_ip)

                # Send completion with token
                completion = create_room_complete(room_name, token, username)
                client_sock.send(encode_tcrp_message(completion))

                print(
                    f"\n✅ Room '{room_name}' crated successfully, token issued to {username}"
                )

        except Exception as e:
            print(f"❌ Error in create_room handler: {e}")

            # Send error response
            error_response = create_room_response(
                room_name, TCRPStatusCodes.SERVER_ERROR, "Internal server error"
            )
            client_sock.send(encode_tcrp_message(error_response))

    def handle_join_room(
        self, client_sock: socket.socket, client_addr: tuple, message: TCRPMessage
    ):
        """Handle room joining request"""
        try:
            # Extract request data
            username = message.payload["username"]
            password = message.payload["password"]
            room_name = message.room_name
            client_ip = client_addr[0]

            # RESPONSE PHASE
            result, result_message, room = self.join_room(
                room_name, username, client_ip, password
            )

            if result:
                response = join_room_response(
                    room_name, TCRPStatusCodes.SUCCESS, result_message
                )
            else:
                # Determine appropriate status code
                if (
                    "not found" in result_message
                    or "no longer active" in result_message
                ):
                    status_code = TCRPStatusCodes.ROOM_NOT_FOUND
                elif "password" in result_message:
                    status_code = TCRPStatusCodes.UNAUTHORIZED
                elif "Invalid" in result_message:
                    status_code = TCRPStatusCodes.INVALID_USERNAME
                else:
                    status_code = TCRPStatusCodes.SERVER_ERROR

                response = join_room_response(room_name, status_code, result_message)

            # Send response
            client_sock.send(encode_tcrp_message(response))

            # COMPLETION phase (only if successful)
            if result and room:
                # Generate token for participant
                token = self.token_manager.create_token(room_name, username, client_ip)

                # Add participant to room
                room.add_participant(token, username, client_ip)

                # Send completion with token
                completion = join_room_complete(
                    room_name, token, room.host_username, room.get_participant_count()
                )
                client_sock.send(encode_tcrp_message(completion))

                print(
                    f"✅ {username} joined room '{room_name}' successfully, token issued"
                )

        except Exception as e:
            print(f"❌ Error in join_room handler: {e}")
            # Send error response
            error_response = join_room_response(
                room_name, TCRPStatusCodes.SERVER_ERROR, "Internal server error"
            )
            client_sock.send(encode_tcrp_message(error_response))

    def create_room(
        self, room_name: str, host_username: str, host_ip: str, password: str = None
    ) -> Tuple[bool, str]:
        """Create a new room"""
        # Validate inputs based on protocol constraints
        if not validate_room_name(room_name):
            return False, "Invalid room name"

        if not validate_username(host_username):
            return False, "Invalid username"

        # Check if room already exists
        if room_name in self.rooms:
            return False, "Room already exists"

        # Create new room
        new_room = Room(room_name, host_username, host_ip, password)

        # Add room to rooms dictionary
        self.rooms[room_name] = new_room

        print(f"🏠 Room '{room_name}' created by {host_username}")
        return True, "Room creation approved"

    def join_room(
        self, room_name: str, username: str, client_ip: str, password: str = None
    ) -> Tuple[bool, str, Optional[Room]]:
        """Join an existing room"""
        # Validate inputs based on protocol constraints
        if not validate_username(username):
            return False, "Invalid username", None

        # Check if room exists
        if room_name not in self.rooms:
            return False, "Room does not exist", None

        # Get room
        room = self.rooms[room_name]

        # Check password
        if not room.validate_password(password):
            return False, "Incorrect password", None

        # Check if host is still active
        if not room.is_host_active():
            del self.rooms[room_name]
            return False, "Room is no longer active", None

        print(f"🚪 {username} joined room '{room_name}'")
        return True, "Join room successful", room

    def cleanup_inactive_rooms(self):
        """Remove rooms where host has disconnected"""
        inactive_rooms = []
        for room_name, room in self.rooms.items():
            if not room.is_host_active():
                inactive_rooms.append(room_name)

        for room_name in inactive_rooms:
            print(f"🗑️ Removing inactive room: '{room_name}'")
            del self.rooms[room_name]

    def stop(self):
        """Stop the TCP server"""
        self.running = False
        if hasattr(self, "sock"):
            self.sock.close()
        print("\n👋 Server shutting down...")


if __name__ == "__main__":
    server = TCRPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
