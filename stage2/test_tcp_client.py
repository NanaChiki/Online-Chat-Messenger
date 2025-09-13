#!/usr/bin/env python3
"""
Simple TCP client to test the room server
"""

import socket
from base64 import encode

from tcp_protocol import *


def test_room_operations():
    """Test room creation and joining"""

    # Test 1: Create a room
    print("\n🧪 Test1: Creating room...")
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(("localhost", 12346))

    create_request = create_room_request("Alice", "TestRoom", "secret123")
    sock1.send(encode_tcrp_message(create_request))

    # Receive response and completion
    response_data = sock1.recv(4096)
    response = decode_tcrp_message(response_data)
    print(f"Response: {response.payload}")

    completion_data = sock1.recv(4096)
    completion = decode_tcrp_message(completion_data)
    print(f"Completion: {completion.payload}")

    sock1.close()

    # Test 2: Join the room
    print("\n🧪 Test 2: Joining room...")
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(("localhost", 12346))

    join_request = join_room_request("Bob", "TestRoom", "secret123")
    sock2.send(encode_tcrp_message(join_request))

    # Receive response and completion
    response_data = sock2.recv(4096)
    response = decode_tcrp_message(response_data)
    print(f"Response: {response.payload}")

    completion_data = sock2.recv(4096)
    completion = decode_tcrp_message(completion_data)
    print(f"Completion: {completion.payload}")

    sock2.close()
    print("\n✅ TCP Server tests completed!")


if __name__ == "__main__":
    test_room_operations()
