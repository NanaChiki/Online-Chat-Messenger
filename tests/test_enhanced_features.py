#!/usr/bin/env python3
"""
Enhanced Feature Tests for Stage 1 Chat Application
Tests the new join functionality, disconnect notifications, and server status features.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
import threading
import time

from stage1.protocol import (
    MSG_TYPE_CHAT,
    MSG_TYPE_JOIN,
    MSG_TYPE_SYSTEM,
    decode_message,
    encode_join_request,
    encode_message,
    encode_system_message,
)


def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{'=' * 70}")
    print(f"🧪 {test_name}")
    print(f"{'=' * 70}")


def test_protocol_enhancements():
    """Test the enhanced protocol with message types"""
    print_test_header("PROTOCOL ENHANCEMENT TESTS")

    print("1️⃣  Testing Join Request Encoding/Decoding")
    join_data = encode_join_request("Alice")
    username, message, msg_type = decode_message(join_data)
    assert username == "Alice"
    assert message == "join"
    assert msg_type == MSG_TYPE_JOIN
    print("✅ Join request protocol works correctly")

    print("\n2️⃣  Testing System Message Encoding/Decoding")
    system_data = encode_system_message("Server is shutting down")
    username, message, msg_type = decode_message(system_data)
    assert username == "SYSTEM"
    assert message == "Server is shutting down"
    assert msg_type == MSG_TYPE_SYSTEM
    print("✅ System message protocol works correctly")

    print("\n3️⃣  Testing Chat Message with Type")
    chat_data = encode_message("Bob", "Hello World", MSG_TYPE_CHAT)
    username, message, msg_type = decode_message(chat_data)
    assert username == "Bob"
    assert message == "Hello World"
    assert msg_type == MSG_TYPE_CHAT
    print("✅ Chat message with type works correctly")


def test_manual_scenarios():
    """Provide manual testing scenarios for the enhanced features"""
    print_test_header("MANUAL TESTING SCENARIOS")

    print("""
🔧 ENHANCED FEATURE TESTING GUIDE:

📋 SCENARIO 1: Join Functionality
1️⃣  Start server: `python stage1/server.py`
2️⃣  Start Client 1: `python stage1/client.py`
   - Username: Alice
   - DON'T type "join" yet
3️⃣  Start Client 2: `python stage1/client.py`
   - Username: Bob
   - Type: "join"
   - ✅ Should see: "🔔 🎉 Bob has joined the chat"
4️⃣  In Alice's terminal, type: "Hello"
   - ✅ Should see: "⚠️ Please type 'join' first to enter the chat!"
5️⃣  In Alice's terminal, type: "join"
   - ✅ Bob should see: "🔔 🎉 Alice has joined the chat"
6️⃣  Now Alice types: "Hello everyone!"
   - ✅ Bob should see: "💬 [Alice]: Hello everyone!"

📋 SCENARIO 2: Disconnect Notifications
1️⃣  With Alice and Bob both joined...
2️⃣  Close Alice's terminal (Ctrl+C)
3️⃣  ✅ Bob should see: "🔔 👋 Alice has left the chat"
4️⃣  ✅ Server should show: "🚪 Alice disconnected from ..."

📋 SCENARIO 3: Server Shutdown/Restart
1️⃣  With clients connected and joined...
2️⃣  Stop server (Ctrl+C in server terminal)
3️⃣  ✅ All clients should see: "🔔 🛑 Server is shutting down. Please wait until it comes back."
4️⃣  ✅ Clients should show: "🔌 Connection lost. Trying to reconnect..."
5️⃣  Restart server: `python stage1/server.py`
6️⃣  ✅ Clients should see: "✅ Connection restored! Please type 'join' to re-enter chat."
7️⃣  Type "join" in each client to rejoin

📋 SCENARIO 4: Multiple Users Join/Leave
1️⃣  Start server and 3 clients (Alice, Bob, Charlie)
2️⃣  Have them join one by one:
   - Alice types "join" → Others see Alice joined
   - Bob types "join" → Others see Bob joined  
   - Charlie types "join" → Others see Charlie joined
3️⃣  Test chat between all three
4️⃣  Have Bob leave (Ctrl+C)
   - ✅ Alice and Charlie see: "🔔 👋 Bob has left the chat"
5️⃣  Continue chatting between Alice and Charlie

📋 SCENARIO 5: Error Handling
1️⃣  Try to chat without joining first
   - ✅ Should see: "⚠️ Please type 'join' first to enter the chat!"
2️⃣  Try to join multiple times
   - ✅ Should work without issues
3️⃣  Test with special characters in messages
4️⃣  Test with very long messages
    """)


def test_load_simulation():
    """Simulate multiple users joining and chatting"""
    print_test_header("LOAD SIMULATION TEST")

    print("""
⚡ SIMULATED LOAD TEST:

This simulates multiple users joining and chatting rapidly.

1️⃣  Start the server: `python stage1/server.py`
2️⃣  Run this simulation script:

```python
import socket
import time
from stage1.protocol import encode_join_request, encode_message, MSG_TYPE_CHAT

# Simulate 5 users joining
for i in range(5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    username = f"User{i}"
    
    # Send join request
    join_data = encode_join_request(username)
    sock.sendto(join_data, ('localhost', 12345))
    
    # Send a chat message
    chat_data = encode_message(username, f"Hello from {username}!", MSG_TYPE_CHAT)
    sock.sendto(chat_data, ('localhost', 12345))
    
    time.sleep(0.1)  # Small delay
    sock.close()
```

3️⃣  Expected results:
   ✅ Server shows all 5 users joining
   ✅ No crashes or errors
   ✅ All join notifications sent
   ✅ All chat messages processed
    """)


def main():
    """Run all enhanced feature tests"""
    print("🚀 Stage 1 Enhanced Features - Test Suite")
    print("Testing: Join functionality, Disconnect notifications, Server status")

    print("\nChoose a test to run:")
    print("1. Protocol Enhancement Tests (automated)")
    print("2. Manual Testing Scenarios")
    print("3. Load Simulation Instructions")
    print("4. Run All")

    choice = input("\nEnter your choice (1-4): ")

    if choice == "1":
        test_protocol_enhancements()
    elif choice == "2":
        test_manual_scenarios()
    elif choice == "3":
        test_load_simulation()
    elif choice == "4":
        test_protocol_enhancements()
        test_manual_scenarios()
        test_load_simulation()
    else:
        print("Invalid choice!")
        return

    print(f"\n{'=' * 70}")
    print("🎯 Testing completed!")
    print("✨ Your enhanced chat application now supports:")
    print("  📥 Explicit join functionality")
    print("  📢 Join/disconnect notifications")
    print("  🔌 Server status messages")
    print("  🔄 Automatic reconnection")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
