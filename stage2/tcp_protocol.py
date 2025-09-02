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
MAX_ROOM_NAME_SIZE = 28  # 2^28 bytes
MAX_OPERATION_PAYLOAD_SIZE = 32  # 2^32 bytes
TOKEN_SIZE = 255  # 255 bytes for secure token


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


##### TODO: Implement the following functions and classes#####
# def encode_tcrp_message(message: TCRPMessage) -> bytes:
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
