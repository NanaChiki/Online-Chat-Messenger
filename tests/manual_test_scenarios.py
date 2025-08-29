# tests/manual_test_scenarios.py - Manual test scenarios
"""
Manual test scenarios for Stage 1 Chat Application
Run this script and follow the instructions to test various scenarios.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
import threading
import time

from stage1.protocol import MAX_MESSAGE_SIZE, MAX_USERNAME_LENGTH, encode_message


def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{'=' * 60}")
    print(f"🧪 {test_name}")
    print(f"{'=' * 60}\n")


def test_edge_cases():
    """Test edge cases for protocol validation"""
    print_test_header("EDGE CASE TESTS")

    print("1️⃣ Testing Long Username (near 255 character limit)")
    long_username = "A" * 250
    try:
        encoded = encode_message(long_username, "Test Message")
        print("✅ Long username test passed")
    except Exception as e:
        print(f"❌ Long username test failed: {e}")

    print("\n2️⃣ Testing Very Long Username (over 255 characters)")
    very_long_username = "A" * 256
    try:
        encoded = encode_message(very_long_username, "Test Message")
        print("❌ Very long username should have failed!")
    except ValueError:
        print("✅ Very long usename correctly rejected")

    print("\n3️⃣ Testing Special Characters and Emojis")
    special_chars = "Hello! 你好 🚀 こんにちは ñáéíóú"
    try:
        encoded = encode_message("TestUser🎉", special_chars)
        print("✅ Special characters test passed")
    except Exception as e:
        print(f"❌ Special characters test failed: {e}")

    print("\n4️⃣ Testing Maximum Message Size")
    username = "Alice"
    # Calculate max message size minus username overhead
    # max_msg_len = (
    #     MAX_MESSAGE_SIZE - 1 - len(username.encode("utf-8")) - 100
    # )  # Safety margin
    max_msg_len = MAX_MESSAGE_SIZE - 2 - len(username.encode("utf-8"))
    long_message = "A" * max_msg_len
    try:
        encoded = encode_message(username, long_message)
        print(encoded)
        print(f"✅ Large message test passed (size: {len(encoded)} bytes)")
    except Exception as e:
        print(f"❌ Large message test failed: {e}")


def test_multi_client_scenarios():
    """Instructions for testing multi-client scenarios"""
    print_test_header("MULTI-CLIENT TESTING INSTRUCTIONS")

    print("""
🔧 SETUP INSTRUCTIONS:

1️⃣  Open 4 terminal windows

2️⃣  Terminal 1 - Start Server:
    cd stage1
    python server.py
    
3️⃣  Terminal 2 - Client Alice:
    cd stage1
    python client.py
    Enter username: Alice
    
4️⃣  Terminal 3 - Client Bob:
    cd stage1
    python client.py  
    Enter username: Bob
    
5️⃣  Terminal 4 - Client Charlie:
    cd stage1
    python client.py
    Enter username: Charlie
    
📝 TEST SCENARIOS:

🎯 Scenario 1: Basic Chat
   - Alice types: "Hello everyone!"
   - ✅ Bob and Charlie should see: "Alice: Hello everyone!"
   - ✅ Alice should NOT see her own message
   
🎯 Scenario 2: Multi-directional Chat  
   - Bob types: "Hi Alice!"
   - Charlie types: "Hey there!"
   - ✅ Everyone should see others' messages
   
🎯 Scenario 3: Client Disconnect
   - Close Alice's terminal (Ctrl+C)
   - Bob types: "Is Alice still here?"
   - ✅ Only Charlie should receive the message
   - ✅ Server should show Alice disconnected
   
🎯 Scenario 4: Client Reconnect
   - Start Alice again with same username
   - Charlie types: "Alice is back!"
   - ✅ Both Alice and Bob should receive message
   
🎯 Scenario 5: Special Characters
   - Try messages with: emojis 🚀🎉, accents áéíóú, other languages 你好
   
🎯 Scenario 6: Long Messages
   - Type a very long message (close to 4096 characters)
   - ✅ Should work correctly
   
🎯 Scenario 7: Server Restart
   - Stop server (Ctrl+C in server terminal)
   - Clients should show connection errors
   - Restart server
   - Start new clients - should work normally
    """)


def run_stress_test():
    """Simple stress test"""
    print_test_header("STRESS TEST")

    print("""
⚡ STRESS TEST INSTRUCTIONS:

This tests the "10,000 packets per second" requirement.

1️⃣  Start the server in one terminal
2️⃣  Run this command in another terminal to simulate rapid messages:

    python3 -c "
    import socket
    import time
    from stage1.protocol import encode_message, encode_join_request, MSG_TYPE_CHAT

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()

    # First, send join requests for test users
    print('Joining test users...')
    for i in range(10):
        username = f'StressUser{i}'
        join_msg = encode_join_request(username)
        sock.sendto(join_msg, ('localhost', 12345))

    time.sleep(0.5)  # Give server time to process joins

    # Now send chat messages
    print('Starting stress test...')
    for i in range(1000):
        username = f'StressUser{i%10}'
        message = f'Stress message {i}'
        chat_msg = encode_message(username, message, MSG_TYPE_CHAT)
        sock.sendto(chat_msg, ('localhost', 12345))
        if i % 100 == 0:
            print(f'Sent {i} messages')

    end_time = time.time()
    duration = end_time - start_time
    rate = 1000 / duration
    print(f'Sent 1000 messages in {duration:.2f} seconds')
    print(f'Rate: {rate:.0f} messages/second')
    sock.close()
"
    "

3️⃣  Expected results:
    ✅ Server should handle all messages
    ✅ No crashes or errors
    ✅ Rate should be well above 100 messages/second
    """)


def main():
    """Run all manual tests"""
    print("🚀 Stage 1 Chat Application - Test Suite")
    print("Choose a test to run:")
    print("1. Edge Case Tests (automated)")
    print("2. Multi-Client Testing Instructions")
    print("3. Stress Test Instructions")
    print("4. Run All")

    choice = input("\nEnter your choice (1-4): ")
    if choice == "1":
        test_edge_cases()
    elif choice == "2":
        test_multi_client_scenarios()
    elif choice == "3":
        run_stress_test()
    elif choice == "4":
        test_edge_cases()
        test_multi_client_scenarios()
        run_stress_test()
    else:
        print("Invalid choice!")
        return

    print(f"\n{'=' * 60}")
    print("🎯 Testing completed!")
    print("If any tests failed, check your implementation.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
