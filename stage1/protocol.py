"""
Online Chat Messenger - Stage 1 Protocol
Protocol definitions and utilities for Stage 1 UDP messaging.
"""

MAX_MESSAGE_SIZE = 4096
MAX_USERNAME_LENGTH = 255


def encode_message(username: str, message: str) -> bytes:
    """
    Encode a message into a byte string according to Stage 1 protocol.
    Format: [username_len(1 byte)][username][message]
    """
    username_bytes = username.encode("utf-8")
    message_bytes = message.encode("utf-8")

    # Validate username length
    if len(username_bytes) > MAX_USERNAME_LENGTH:
        raise ValueError(
            f"Username too long: {len(username_bytes)} > {MAX_USERNAME_LENGTH}"
        )

    # Create the packet: [username_len(1 byte)][username][message]
    packet = bytes([len(username_bytes)]) + username_bytes + message_bytes
    if len(packet) > MAX_MESSAGE_SIZE:
        raise ValueError(f"Message too long: {len(packet)} > {MAX_MESSAGE_SIZE}")

    return packet


def decode_message(data: bytes) -> tuple[str, str]:
    """
    Decode a message from a byte string according to Stage 1 protocol.
    Returns: (username, message)
    """

    if len(data) < 1:
        raise ValueError("Invalid message: too short")

    username_len = data[0]
    if len(data) < 1 + username_len:
        raise ValueError("Invalid message: incomplete username")

    username = data[1 : 1 + username_len].decode("utf-8")
    message = data[1 + username_len :].decode("utf-8")

    return username, message
