#! /usr/bin/env python3
"""
UDP Protocol for Stage 2 Chat Room Messaging
Handles room-scoped chat communication with token validation
"""

import struct
from typing import Optional, Tuple

# Protocol Constants
MAX_PACKET_SIZE_CLIENT_TO_SERVER = 4096  # MAX client-server packet
MAX_PACKET_SIZE_SERVER_TO_CLIENT = 4094  # MAX server-client packet
MAX_ROOM_NAME_SIZE = 255  # MAX room name bytes
MAX_TOKEN_SIZE = 255  # MAX token bytes
HEADER_SIZE = 2

# Message size calculation
MAX_MESSAGE_SIZE = (
    MAX_PACKET_SIZE_CLIENT_TO_SERVER - HEADER_SIZE - MAX_ROOM_NAME_SIZE - MAX_TOKEN_SIZE
)

# Server-to-client Message Types
MSG_TYPE_CHAT = 1
MSG_TYPE_SYSTEM = 2
MSG_TYPE_USER_JOIN = 3
MSG_TYPE_USER_LEAVE = 4


class UDPChatMessage:
    """Represents a UDP chat message with room and token info"""

    def __init__(self, room_name: str, token: str, message: str):
        self.room_name = room_name
        self.token = token
        self.message = message

    def __repr__(self):
        return f"UDPChatMessage(room='{self.room_name}', token='{self.token[:8]}...', message='{self.message[:50]}...')"


def encode_udp_message(room_name: str, token: str, message: str) -> bytes:
    """
    Encode a client-to-server UDP message

    Format: Header(2 bytes) + Body(variable)
    Header: RoomNameSize(1) | TokenSize(1)
    Body: RoomName + Token + Message

    Args:
        room_name: Chat room name (max 255 bytes UTF-8)
        token: Authentication token (max 255 bytes)
        message: Chat message content

    Returns:
        Encoded UDP packet bytes

    Raises:
        ValueError: If constrains are violated
    """
    # Encode strings to UTF-8 bytes
    room_name_bytes = room_name.encode("utf-8")
    token_bytes = token.encode("utf-8")
    message_bytes = message.encode("utf-8")

    # Validate sizes
    if len(room_name_bytes) > MAX_ROOM_NAME_SIZE:
        raise ValueError(
            f"Room name too long: {len(room_name_bytes)} > {MAX_ROOM_NAME_SIZE}"
        )
    if len(token_bytes) > MAX_TOKEN_SIZE:
        raise ValueError(f"Token too long: {len(token_bytes)} > {MAX_TOKEN_SIZE}")

    # Calculate total packet size
    total_packet_size = (
        HEADER_SIZE + len(room_name_bytes) + len(token_bytes) + len(message_bytes)
    )
    if total_packet_size > MAX_PACKET_SIZE_CLIENT_TO_SERVER:
        raise ValueError(
            f"Packet too large: {total_packet_size} > {MAX_PACKET_SIZE_CLIENT_TO_SERVER}"
        )

    # Packet header: RoomNameSize(1) + TokenSize(1)
    header = struct.pack("BB", len(room_name_bytes), len(token_bytes))

    # Combine header + body
    packet = header + room_name_bytes + token_bytes + message_bytes

    return packet


def decode_udp_message(packet: bytes) -> UDPChatMessage:
    """
    Decode a client-to-server UDP message

    Args: Raw UDP packet bytes

    Returns:
         UDPChatMessage object

    Raises:
        ValueError: If packet format is invalid
    """
    # Validate minimum packet size
    if len(packet) < HEADER_SIZE:
        raise ValueError(f"Packet too small: {len(packet)} < {HEADER_SIZE}")

    # Unpack header: RoomNameSize(1) + TokenSize(1)
    room_name_size, token_size = struct.unpack("BB", packet[:HEADER_SIZE])

    # Validate header values
    if room_name_size > MAX_ROOM_NAME_SIZE:
        raise ValueError(f"Invalid room name size: {room_name_size}")
    if token_size > MAX_TOKEN_SIZE:
        raise ValueError(f"Invalid token size: {token_size}")

    # Calculate expected packet size
    expected_size = HEADER_SIZE + room_name_size + token_size
    if len(packet) < expected_size:
        raise ValueError(f"Packet incomplete: {len(packet)} < {expected_size}")

    # Extract body parts
    offset = HEADER_SIZE
    room_name_bytes = packet[offset : offset + room_name_size]
    offset += room_name_size

    token_bytes = packet[offset : offset + token_size]
    offset += token_size

    message_bytes = packet[offset:]

    # Decode UTF-8 strings
    try:
        room_name_string = room_name_bytes.decode("utf-8")
        token_string = token_bytes.decode("utf-8")
        message_string = message_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid UTF-8 encoding: {e}")

    return UDPChatMessage(room_name_string, token_string, message_string)


class UDPServerMessage:
    """Represents a server-to-client UDP message"""

    def __init__(self, msg_type: int, username: str, message: str):
        self.msg_type = msg_type
        self.username = username
        self.message = message

    def __repr__(self):
        type_names = {1: "CHAT", 2: "SYSTEM", 3: "JOIN", 4: "LEAVE"}
        type_name = type_names.get(self.msg_type, "UNKNOWN")
        return f"UDPServerMessage({type_name}, '{self.username}', '{self.message[:30]}...')"


def encode_server_message(msg_type: int, username: str, message: str) -> bytes:
    """
    Encode a server-to-client UDP message

    Format: Header(3 bytes) + Body(variable)
    Header: MessageType(1) | UsernameSize(1) | MessageSize(1)
    Body: Username + Message

    Returns:
        Encoded UDP packet bytes (max 4094 bytes)
    """
    username_bytes = username.encode("utf-8")
    message_bytes = message.encode("utf-8")

    # Validate sizes
    if len(username_bytes) > 255:
        raise ValueError(f"Username too long: {len(username_bytes)} > 255")
    if len(message_bytes) > 255:
        raise ValueError(f"Message too long: {len(message_bytes)} > 255")

    total_size = 3 + len(username_bytes) + len(message_bytes)
    if total_size > MAX_PACKET_SIZE_SERVER_TO_CLIENT:
        raise ValueError(
            f"Packet too large: {total_size} > {MAX_PACKET_SIZE_SERVER_TO_CLIENT}"
        )

    # Packet header: MessageType(1) + UsernameSize(1) + MessageSize(1)
    header = struct.pack("BBB", msg_type, len(username_bytes), len(message_bytes))

    return header + username_bytes + message_bytes


def decode_server_message(packet: bytes) -> UDPServerMessage:
    """
    Decode a server-to-client UDP message

    returns:
        UDPServerMessage object
    """
    if len(packet) < 3:
        raise ValueError(f"Packet too small: {len(packet)} < 3")

    msg_type, username_size, message_size = struct.unpack("BBB", packet[:3])

    if len(packet) < 3 + username_size + message_size:
        raise ValueError("Packet incomplete")

    username_string = packet[3 : 3 + username_size].decode("utf-8")
    message_string = packet[
        3 + username_size : 3 + username_size + message_size
    ].decode("utf-8")

    return UDPServerMessage(msg_type, username_string, message_string)


def test_upd_protocol():
    """Test UDP protocol encoding/decoding functions"""
    print("Testing UDP protocol...")

    # Test 1: Basic client-to-server message
    try:
        room_name = "general"
        token = "abc123"
        message = "This is test 1"

        packet = encode_udp_message(room_name, token, message)
        decoded = decode_udp_message(packet)

        assert decoded.room_name == room_name
        assert decoded.token == token
        assert decoded.message == message
        print("✅ Test 1: Basic message encoding/decoding passed")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Server-to-client messages
    try:
        for msg_type, type_name in [
            (MSG_TYPE_CHAT, "CHAT"),
            (MSG_TYPE_SYSTEM, "SYSTEM"),
        ]:
            username = "alice"
            message = f"This is a {type_name} message"

            packet = encode_server_message(msg_type, username, message)
            encoded = decode_server_message(packet)

            assert encoded.msg_type == msg_type
            assert encoded.username == username
            assert encoded.message == message
        print("✅ Test 2: Server message types passed")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Unicode support
    try:
        packet = encode_udp_message("部屋", "トークン", "こんにちは！🎉")
        decoded = decode_udp_message(packet)

        assert decoded.room_name == "部屋"
        assert decoded.message == "こんにちは！🎉"
        print("✅ Test 3: Unicode support passed")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    # Test 4: Error handling
    try:
        # Test oversized room name
        long_name = "x" * 300
        encode_udp_message(long_name, "token", "msg")
        print("❌ Test 4a: Should have failed on long room name")
    except ValueError:
        print("✅ Test 4a: Long room name rejection passed")

    try:
        # Test invalid packet
        decode_udp_message(b"x")
        print("❌ Test 4b: Should have failed on invalid packet")
    except ValueError:
        print("✅ Test 4b: Invalid packet rejection passed")

    print("🎯 UDP Protocol testing complete!\n")


if __name__ == "__main__":
    test_upd_protocol()
