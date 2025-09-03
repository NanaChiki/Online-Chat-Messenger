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

    Header (32 bytes): RoomNameSize (1 byte), Operation (1 byte), State (1 byte), OperationPayloadSize (29 bits, stored in 4 bytes; header padded to 32 bytes)
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
    room_name_size = len(room_name_bytes)
    operation = int(message.operation.value)
    state = int(message.state.value)
    payload_size = len(payload_bytes)

    # Pack header: 1 byte + 1 byte + 1 byte + 29 bits for payload size
    header = struct.pack(">BBB", room_name_size, operation, state)

    # Payload size as 29 bits (I'll use 4 bytes but mask to 29 bits)
    payload_size_bytes = struct.pack(">I", payload_size & 0x1FFFFFFF)  # Mask to 29 bits
    # Take only the last 29 bits (effectively 4 bytes, but spec says 29)
    header += payload_size_bytes

    # Pad header to exactly 32 bytes
    header = header.ljust(HEADER_SIZE, b"\x00")

    # Combine header and body
    return header + room_name_bytes + payload_bytes


##### TODO: Implement the following functions and classes#####
# def decode_tcrp_message(data: bytes) -> TCRPMessage:
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
