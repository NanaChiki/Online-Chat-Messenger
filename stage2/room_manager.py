#! /usr/bin/env python3
"""
Room manager for chat rooms. Manages room state and participants.
"""

import time


class Room:
    """Represents a chat room with participants and metadata"""

    def __init__(
        self, name: str, host_username: str, host_ip: str, password: str = None
    ):
        self.name = name
        self.host_username = host_username
        self.host_ip = host_ip
        self.password = password
        self.created_at = time.time()

        # Participants: { token: { username, ip, joined_at}}
        self.participants = {}

        # Host gets the first token
        self.host_token = None

    def add_participant(self, token: str, username: str, ip: str) -> bool:
        """Add a participant to the room"""
        self.participants[token] = {
            "username": username,
            "ip": ip,
            "joined_at": time.time(),
            "is_host": username == self.host_username,
        }

        if username == self.host_username:
            self.host_token = token

        return True

    def remove_participant(self, token: str) -> bool:
        """Remove a participant from the room"""
        if token in self.participants:
            del self.participants[token]
            return True
        return False

    def is_host_active(self) -> bool:
        """Check if the room host is still active"""
        return self.host_token is not None and self.host_token in self.participants

    def get_participant_count(self) -> int:
        """Get current number of participants in the room"""
        return len(self.participants)

    def validate_password(self, password: str) -> bool:
        """Validate room password"""
        if self.password is None:
            return password is None
        return self.password == password

    def __repr__(self):
        return f"Room(name='{self.name}', host='{self.host_username}', host_ip='{self.host_ip}', password='{self.password}', created_at='{self.created_at}', participants='{self.get_participant_count()}')"
