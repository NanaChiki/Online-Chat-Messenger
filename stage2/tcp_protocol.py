# stage2/tcp_protocol.py

#! /usr/bin/env python3
"""
TCP Chat Room Protocol (TCRP) Implementation for Stage 2
Handles room creation, joining, and token management via reliable TCP connections.
"""

import hashlib
import json
import struct
from enum import IntEnum
from typing import Any, Dict, Optional, Tuple

# Protocol Constants
HEADER_SIZE = 32  # 32 bytes for the header
MAX_ROOM_NAME_SIZE = 255  # 2**8 - 1 bytes
MAX_OPERATION_PAYLOAD_SIZE = 536870911  # 2**29 - 1 bytes
TOKEN_SIZE = 32  # 32 bytes for secure token (up to 255 bytes)


# A custom protocol called The Chat Room Protocol (TCRP)
class TCRPOperation(IntEnum):
    """TCRP Operation codes"""

    CREATE_ROOM = 1
    JOIN_ROOM = 2


class TCRPState(IntEnum):
    """TCRP State codes"""

    REQUEST = 0  # Client sends initial request
    RESPONSE = 1  # Server responses with status code
    COMPLETION = 2  # Server sends unique token


class TCRPStatusCodes(IntEnum):
    """Status codes for server responses"""

    SUCCESS = 0
    ROOM_EXISTS = 1
    ROOM_NOT_FOUND = 2
    ROOM_FULL = 3
    INVALID_USERNAME = 4
    INVALID_NAME = 5
    SERVER_ERROR = 6
    UNAUTHORIZED = 7


class TCRPMessage:
    """Represents a TCRP message with header and body"""

    def __init__(
        self,
        room_name: str,
        operation: TCRPOperation,
        state: TCRPState,
        payload: Any = None,
    ):
        self.room_name = room_name
        self.operation = operation
        self.state = state
        self.payload = payload or {}

    def __repr__(self):
        return f"TCRPMessage(room_name={self.room_name}, operation={self.operation.name}, state={self.state.name})"


def encode_tcrp_message(message: TCRPMessage) -> bytes:
    """
    Encode a TCRP message into bytes according to the protocol specification.

    Header (32 bytes): RoomNameSize (1 byte), Operation (1 byte), State (1 byte), OperationPayloadSize (29 bytes)
    Body: [RoomName(max 255 bytes), OperationPayload(max 536870911 bytes)]

    Args:
        message: TCRPMessage to encode

    Returns:
        bytes: Encoded TCRP message

    Raises:
        ValueError: If message exceeds size limits
    """
    # Encode room name
    room_name_bytes = message.room_name.encode("utf-8")
    if len(room_name_bytes) > MAX_ROOM_NAME_SIZE:
        raise ValueError(
            f"Room name too long {len(room_name_bytes)} > {MAX_ROOM_NAME_SIZE}"
        )

    # Encode payload as JSON string
    if isinstance(message.payload, dict):
        payload_bytes = json.dumps(message.payload).encode(
            "utf-8"
        )  # Convert to JSON string, then encode to bytes
    elif isinstance(message.payload, str):
        payload_bytes = message.payload.encode("utf-8")  # Convert to bytes directory
    else:
        payload_bytes = str(message.payload).encode(
            "utf-8"
        )  # Convert to string, then encode to bytes

    if len(payload_bytes) > MAX_OPERATION_PAYLOAD_SIZE:
        raise ValueError(
            f"Payload too long {len(payload_bytes)} > {MAX_OPERATION_PAYLOAD_SIZE}"
        )

    # Create header (32 bytes)
    # RoomNameSize(1) + Operation(1) + State(1) + OperationPayloadSize(29)
    room_name_size = len(room_name_bytes)  # The number of bytes of the UTF-8 room name
    operation = int(message.operation.value)
    state = int(message.state.value)
    payload_size = len(payload_bytes)  # The number of bytes in the payload

    # Pack header: 1 byte + 1 byte + 1 byte + 29 bytes for payload size
    header = struct.pack(">BBB", room_name_size, operation, state)

    # 29-byte big-endian payload size (Produces a 29-byte representation with leading zeros.)
    # Example: 5 becomes 28 zero bytes + \x05.
    payload_size_bytes = payload_size.to_bytes(29, "big")
    header += payload_size_bytes  # Header is now exactly 32 bytes

    body = room_name_bytes + payload_bytes

    # Combine header and body
    return header + body


def decode_tcrp_message(data: bytes) -> TCRPMessage:
    """
    Decode bytes into a TCRP message according to the protocol specification.

    Args:
        data: Raw bytes to decode

    Returns:
        TCRPMessage: Decoded TCRP message

    Raises:
        ValueError: If data is invalid or corrupted
    """

    if len(data) < HEADER_SIZE:
        raise ValueError(f"Message too short: {len(data)} < {HEADER_SIZE}")

    # Unpack header (32 bytes)
    header = data[:HEADER_SIZE]

    # Unpack header components
    # (e.g., b'\x05\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05roomaaaaa')
    room_name_size = header[0]
    operation = TCRPOperation(header[1])  # e.g., <TCRPOperation.CREATE_ROOM: 1>
    state = TCRPState(header[2])  # e.g., <TCRPState.REQUEST: 0>

    # Extract payload size bytes and then converts to integer
    payload_size_bytes = header[3:32]
    payload_size = int.from_bytes(payload_size_bytes, "big")

    # Validate message length
    expected_length = HEADER_SIZE + room_name_size + payload_size
    if len(data) < expected_length:
        raise ValueError(f"Message incomplete: {len(data)} < {expected_length}")

    # Extract body components
    body_start = HEADER_SIZE
    room_name_end = body_start + room_name_size
    payload_end = room_name_end + payload_size

    # Decode room name
    room_name = data[body_start:room_name_end].decode("utf-8")

    if payload_size > 0:
        payload_bytes = data[room_name_end:payload_end]
        try:
            # Try to decode as JSON first
            payload = json.loads(payload_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # If JSON fails, try to decode as string
            payload = payload_bytes.decode("utf-8")
    else:
        payload = {}

    return TCRPMessage(room_name, operation, state, payload)


##### TODO: Implement the following functions and classes#####
# def create_room_request(username: str, room_name: str, password: str = None) -> TCRPMessage:
# def create_room_response(room_name: str, status_code: TCRPStatusCodes, message: str = "") -> TCRPMessage:
# def create_room_complete(room_name: str, token: str, host_username: str) -> TCRPMessage:
# def join_room_request(username: str, room_name: str, password: str = None) -> TCRPMessage:
# def join_room_response(room_name: str, status_code: TCRPStatusCodes, message: str = "") -> TCRPMessage:
# def join_room_complete(room_name: str, token: str, host_username: str, participant_count: int) -> TCRPMessage:
# def generate_secure_token() -> str:
# def validate_room_name(room_name: str) -> bool:
# def validate_username(username: str) -> bool:

# class TokenManager:
# def test_protocol():
# if __name__ == "__main__":
#     test_protocol()
