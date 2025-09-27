#!/usr/bin/env python3
"""
Unified Stage 2 Chat Server
Combines TCP (room management) and UDP (real-time chat) servers
"""

import signal
import sys
import threading
import time
from typing import Dict

from room_manager import Room
from tcp_protocol import TokenManager
from tcp_server import TCRPServer
from udp_server import UDPChatServer


class Stage2ChatServer:
    """
    Unified server that runs both TCP and UDP servers with shared state

    Architecture:
    - TCP server (port 12346): Room creation/joining
    - UDP server (port 12347): Real-time chat messaging
    - Shared state: Rooms and token management
    """

    def __init__(
        self, host: str = "localhost", tcp_port: int = 12346, udp_port: int = 12347
    ):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port

        print("\n🚀 Initializing Unified Stage 2 Chat Server...")
        print(f"📍 Host: {self.host}")
        print(f"🔌 TCP Port: {self.tcp_port} (Room Management)")
        print(f"🔌 UDP Port: {self.udp_port} (Real-time Chat)")

        # Shared state - this is the key integration point
        self.rooms: Dict[str, Room] = {}
        self.token_manager = TokenManager()

        # Server instances
        self.tcp_server = TCRPServer(host, tcp_port)
        self.udp_server = UDPChatServer(host, udp_port)

        # Threading
        self.tcp_thread = None
        self.udp_thread = None
        self.running = False

        print("\n✅ Server components initialized")

    def start(self):
        """Start both TCP and UDP servers with shared state"""
        try:
            print("\n🔧 Configuring shared state...")

            # Shared state between servers
            self._setup_shared_state()

            print("\n🚀 Starting TCP and UDP servers...")

            # Start TCP server in separate thread
            self.tcp_thread = threading.Thread(
                target=self.tcp_server.start, daemon=False, name="TCPServerThread"
            )
            self.tcp_thread.start()

            # Give TCP server time to bind
            time.sleep(0.5)

            # Start UDP server in separate thread
            self.udp_thread = threading.Thread(
                target=self.udp_server.start, daemon=False, name="UDPServerThread"
            )
            self.udp_thread.start()

            # Give UDP server time to bind
            time.sleep(0.5)

            self.running = True
            print("\n🎉 Unified Stage 2 Chat Server is RUNNING!")
            print("📋 Status:")
            print(f"  🟢 TCP Server: {self.host}:{self.tcp_port}")
            print(f"  🟢 UDP Server: {self.host}:{self.udp_port}")
            print("\n💡 Ready for:")
            print("  👥 Room creation/joining (TCP)")
            print("  💬 Real-time Chat (UDP)")
            print("\n Press Ctrl+C to stop servers")

            # Keep main thread alive and monitor servers
            self._monitor_servers()

        except Exception as e:
            print(f"🔴 Failed to start unified server: {e}")
            self.stop()
            sys.exit(1)

    def _setup_shared_state(self):
        """Configure shared state between TCP and UDP servers"""

        # TCP server: Replace its instances with shared ones
        self.tcp_server.rooms = self.rooms
        self.tcp_server.token_manager = self.token_manager

        # UDP server: Inject shared state
        self.udp_server.set_shared_state(self.rooms, self.token_manager)

        print("\n🔗 Shared state configured: ")
        print(f"  📊 Rooms: {id(self.rooms)} (shared)")
        print(f"  🔑 Token Manager: {id(self.token_manager)} (shared)")

    def _monitor_servers(self):
        """Monitor server health and handle shutdown"""
        try:
            while self.running:
                # Check if both servers are still running
                if self.tcp_thread and not self.tcp_thread.is_alive():
                    print("\n🔴 TCP server thread died!")
                    break
                if self.udp_thread and not self.udp_thread.is_alive():
                    print("\n🔴 UDP server thread died!")
                    break

                # Display periodic status
                room_count = len(self.rooms)
                token_count = (
                    len(self.token_manager.tokens) if self.token_manager else 0
                )

                if room_count > 0 or token_count > 0:
                    print(
                        f"\n📊 Status: {room_count} active rooms, {token_count} active tokens"
                    )

                time.sleep(5)  # Status update every 5 seconds

        except KeyboardInterrupt:
            print("\n🛑 Shutdown signal received...")
            self.stop()

        finally:
            self.stop()

    def stop(self):
        """Gracefully stop both servers"""
        if not self.running:
            return

        print("\n🛑 Stopping Unified Stage 2 Chat Server...")
        self.running = False

        # Stop both servers
        if self.tcp_server:
            try:
                self.tcp_server.stop()
                print("\n✅ TCP server stopped")
            except Exception as e:
                print(f"⚠️ Error stopping TCP server: {e}")

        if self.udp_server:
            try:
                self.udp_server.stop()
                print("\n✅ UDP server stopped")
            except Exception as e:
                print(f"⚠️ Error stopping UDP server: {e}")

        # Wait for threads to finish
        if self.tcp_thread and self.tcp_thread.is_alive():
            print("\n⏳ Waiting for TCP server thread...")
            self.tcp_thread.join(timeout=2.0)

        if self.udp_thread and self.udp_thread.is_alive():
            print("\n⏳ Waiting for UDP server thread...")
            self.udp_thread.join(timeout=2.0)

        print("\n✅ Unified Stage 2 Chat Server stopped")


def setup_signal_handlers(server: Stage2ChatServer):
    """Setup graceful shutdown on system signals"""

    def signal_handler(signum, frame):
        print(f"\n🔔 Received signal {signum}")
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)  # Ctrl + C
    signal.signal(signal.SIGTERM, signal_handler)  # Kill command


if __name__ == "__main__":
    # Create and start the unified server
    server = Stage2ChatServer(host="localhost", tcp_port=12346, udp_port=12347)

    # Setup graceful shutdown
    setup_signal_handlers(server)

    try:
        server.start()
    except Exception as e:
        print(f"🔴 Server failed: {e}")
        server.stop()
        sys.exit(1)
