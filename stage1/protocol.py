"""
Online Chat Messenger - Stage 1 Protocol
Protocol definitions and utilities for Stage 1 UDP messaging.
"""

MAX_MESSAGE_SIZE = 4096
MAX_USERNAME_LENGTH = 255

# Message types
MSG_TYPE_CHAT = 0  # Regular chat message
MSG_TYPE_JOIN = 1  # Join request
MSG_TYPE_SYSTEM = 2  # System notification
MSG_TYPE_HEARTBEAT = 3  # Connection heartbeat
MSG_TYPE_DISCONNECT = 4  # Disconnect notification


def encode_message(username: str, message: str, msg_type: int = MSG_TYPE_CHAT) -> bytes:
    """
    Encode a message according to Stage 1 protocol.
    Format: [msg_type(1 byte)][username_len(1 byte)][username][message]
    """
    username_bytes = username.encode("utf-8")
    message_bytes = message.encode("utf-8")

    # Validate username length
    if len(username_bytes) > MAX_USERNAME_LENGTH:
        raise ValueError(
            f"Username too long: {len(username_bytes)} > {MAX_USERNAME_LENGTH}"
        )

    # Create the packet: [msg_type][username_len][username][message]
    packet = bytes([msg_type, len(username_bytes)]) + username_bytes + message_bytes
    if len(packet) > MAX_MESSAGE_SIZE:
        raise ValueError(f"Message too long: {len(packet)} > {MAX_MESSAGE_SIZE}")

    return packet


def decode_message(data: bytes) -> tuple[str, str, int]:
    """
    Decode a message according to Stage 1 protocol.
    Returns: (username, message, msg_type)
    """
    if len(data) < 2:
        raise ValueError("Invalid message: too short")

    msg_type = data[0]
    username_len = data[1]

    if len(data) < 2 + username_len:
        raise ValueError("Invalid message: incomplete username")

    username = data[2 : 2 + username_len].decode("utf-8")
    message = data[2 + username_len :].decode("utf-8")

    return username, message, msg_type


def encode_system_message(message: str) -> bytes:
    """
    Encode a system notification message.
    """
    return encode_message("SYSTEM", message, MSG_TYPE_SYSTEM)


def encode_join_request(username: str) -> bytes:
    """
    Encode a join request message.
    """
    return encode_message(username, "join", MSG_TYPE_JOIN)


def encode_disconnect_request(username: str) -> bytes:
    """
    Encode a disconnect request message.
    """
    return encode_message(username, "disconnect", MSG_TYPE_DISCONNECT)
