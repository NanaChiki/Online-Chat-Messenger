"""
Online Chat Messenger - Stage 1 Protocol
Protocol definitions and utilities for Stage 1 UDP messaging.
"""

MAX_MESSAGE_SIZE = 4096
MAX_USERNAME_LENGTH = 255


def encode_message(username: str, message: str) -> bytes:
    """
    Encode a message into a byte string according to Stage 1 protocol.
    Format: [username_len(1 byte)][username][username][message]
    """
    # Implementation to be added
    pass


def decode_message(data: bytes) -> tuple[str, str]:
    """
    Decode a message from a byte string according to Stage 1 protocol.
    Returns: (username, message)
    """
    # Implementation to be added
    pass
