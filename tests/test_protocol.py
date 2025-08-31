# tests/test_protocol.py - Unit tests for protocol functions
"""
Test suite for Stage 1 Protocol functionality
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from stage1.protocol import (
    MAX_MESSAGE_SIZE,
    MAX_USERNAME_LENGTH,
    MSG_TYPE_CHAT,
    decode_message,
    encode_message,
)


class TestProtocol(unittest.TestCase):
    def test_basic_encoding_decoding(self):
        """Test basic message encoding and decoding"""
        username = "Alice"
        message = "Hello, world!"

        # Encode message
        encoded = encode_message(username, message)

        # Decode message
        decoded_username, decoded_message, decoded_msg_type = decode_message(encoded)

        # Verify encoding and decoding
        self.assertEqual(username, decoded_username)
        self.assertEqual(message, decoded_message)
        self.assertEqual(MSG_TYPE_CHAT, decoded_msg_type)

    def test_empty_message(self):
        """Test encoding/decoding with empty message"""
        username = "Bob"
        message = ""

        encoded = encode_message(username, message)
        decoded_username, decoded_message, decoded_msg_type = decode_message(encoded)

        self.assertEqual(username, decoded_username)
        self.assertEqual(message, decoded_message)
        self.assertEqual(decoded_msg_type, MSG_TYPE_CHAT)

    def test_special_characters(self):
        """Test UTF-8 special characters and emojis"""
        username = "Alice🚀"
        message = "Hello! 你好 🎉 こんにちは"

        encoded = encode_message(username, message)
        decoded_username, decoded_message, decoded_msg_type = decode_message(encoded)

        self.assertEqual(username, decoded_username)
        self.assertEqual(message, decoded_message)
        self.assertEqual(decoded_msg_type, MSG_TYPE_CHAT)

    def test_max_username_length(self):
        """Test maximum username length (255 bytes)"""
        # Create username close to max length
        username = "A" * 250  # 250 ASCII characters == 250 bytes
        message = "Test message"

        encoded = encode_message(username, message)
        decoded_username, decoded_message, decoded_msg_type = decode_message(encoded)

        self.assertEqual(username, decoded_username)
        self.assertEqual(message, decoded_message)
        self.assertEqual(decoded_msg_type, MSG_TYPE_CHAT)

    def test_username_too_long(self):
        """Test username length validation"""
        # Create username longer than max length
        username = "A" * (MAX_USERNAME_LENGTH + 1)
        message = "Test message"

        with self.assertRaises(ValueError):
            encode_message(username, message, MSG_TYPE_CHAT)

    def test_max_message_size(self):
        """Test message size validation"""
        username = "Alice"
        # Create message that approaches max size
        max_message_len = MAX_MESSAGE_SIZE - len(username.encode("utf-8")) - 2
        message = "A" * max_message_len

        encoded = encode_message(username, message)
        decoded_username, decoded_message, decoded_msg_type = decode_message(encoded)

        self.assertEqual(username, decoded_username)
        self.assertEqual(message, decoded_message)
        self.assertEqual(decoded_msg_type, MSG_TYPE_CHAT)

    def test_message_too_long(self):
        """Test message size validation"""
        username = "Alice"
        # Create message that's too long
        message = "A" * MAX_MESSAGE_SIZE

        with self.assertRaises(ValueError):
            encode_message(username, message)

    def test_invalid_decode_data(self):
        """Test decoding invalid data"""
        # Test with empty data
        with self.assertRaises(ValueError):
            decode_message(b"")
        # Data too short for username
        with self.assertRaises(ValueError):
            decode_message(
                b"\x05ABC"
            )  # Says username is 5 bytes long but only 3 bytes are provided


if __name__ == "__main__":
    unittest.main()
