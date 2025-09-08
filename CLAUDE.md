# CLAUDE.md - Project Context for AI Assistant

## 📋 Project Overview
**Online Chat Messenger** - Multi-stage network programming project demonstrating client-server architecture evolution from basic UDP chat to advanced room-based TCP/UDP hybrid system.

## 🎯 Current Status: Stage 2 Implementation
**Last Updated**: September 2024
**Current Focus**: TCP Chat Room Protocol (TCRP) implementation

### ✅ Completed
- **Stage 1**: Full UDP-based chat system with client management
- **Stage 2 Foundation**: 
  - Project structure setup (stage2/ directory)
  - TCRP protocol specification (docs/stage2-specification.md)
  - Protocol constants and enums (tcp_protocol.py)
  - Message classes and status codes
- **tcp_protocol.py**: ~95% complete
  - ✅ Constants, enums, TCRPMessage class
  - ✅ Complete encode/decode functions with 32-byte header support
  - ✅ All helper functions (create_room_*, join_room_*, validation)
  - ✅ Secure token generation with secrets.token_hex
  - ⏳ TODO: TokenManager class, test functions

### 🚧 In Progress
- **Next Phase**: Server implementation (tcp_server.py, udp_server.py)

### 📅 Next Steps
1. Implement TokenManager class and test functions in tcp_protocol.py
2. Implement tcp_server.py and udp_server.py
3. Build room_manager.py for room state management
4. Create client.py for Stage 2 client

## 🏗️ Architecture

### Stage 1 (Complete)
- **Protocol**: Custom UDP protocol
- **Files**: stage1/{server.py, client.py, protocol.py}
- **Features**: Basic chat, disconnect handling, reconnection

### Stage 2 (Current)
- **Dual Protocol**: TCP for room management + UDP for messaging
- **Key Files**:
  - `stage2/tcp_protocol.py` - TCRP implementation
  - `stage2/tcp_server.py` - Room creation/joining server
  - `stage2/udp_server.py` - Real-time messaging server
  - `stage2/room_manager.py` - Room state management
  - `stage2/client.py` - Stage 2 client

## 🛠️ Development Commands

### Testing
```bash
# Stage 1 testing (works)
cd stage1
python server.py  # Terminal 1
python client.py  # Terminal 2+

# Stage 2 testing (in development)
cd stage2
python tcp_server.py  # When implemented
python udp_server.py  # When implemented
python client.py      # When implemented
```

### Git Workflow
- **Main branch**: `master`
- **Remote**: `git@github.com:NanaChiki/Online-Chat-Messenger.git`
- **Commit style**: `feat:`, `fix:`, `docs:` prefixes

## 📋 Protocol Specifications

### Stage 2 TCRP (TCP Chat Room Protocol)
- **Header**: 32 bytes (RoomNameSize + Operation + State + PayloadSize)
- **Max Room Name**: 255 bytes
- **Max Username**: 255 bytes
- **Max Payload**: 536,870,911 bytes (2^29 - 1)
- **Token Size**: 32 bytes (64 hex chars)
- **Operations**: CREATE_ROOM (1), JOIN_ROOM (2)
- **States**: REQUEST (0), RESPONSE (1), COMPLETION (2)
- **Status Codes**: SUCCESS, ROOM_EXISTS, ROOM_NOT_FOUND, ROOM_FULL, INVALID_USERNAME, INVALID_NAME, SERVER_ERROR, UNAUTHORIZED

### Protocol Implementation Status
✅ **All Constants Fixed**:
- `MAX_OPERATION_PAYLOAD_SIZE = 536870911` (correct)
- `MAX_USERNAME_SIZE = 255` (added)
- All protocol limits properly implemented

## 🚨 Important Notes

### Security
- Token-IP binding for authentication
- No credential harvesting allowed
- Defensive security tasks only

### Code Style
- Python 3.8+ compatibility
- Type hints preferred
- Minimal comments unless requested
- Follow existing patterns from Stage 1

### Files to Reference
- `docs/stage2-specification.md` - Complete Stage 2 requirements
- `stage1/protocol.py` - Reference protocol implementation pattern
- `stage1/server.py` - Server architecture reference

## 🎯 Common Tasks
1. **Continue Stage 2**: Focus on server implementation (tcp_server.py)
2. **Complete tcp_protocol.py**: Implement TokenManager class and test functions
3. **Testing**: Create comprehensive test cases for TCRP protocol
4. **Git Management**: Concise commits, push to origin/master

## 📝 Recent Updates (Sept 2024)
- **tcp_protocol.py**: Added complete helper function suite
- **Security**: Implemented cryptographically secure token generation
- **Validation**: Added comprehensive room name and username validation
- **Protocol**: Fixed all constant values to match specification

## 💡 Development Tips
- Check specification first before implementing
- Use existing Stage 1 patterns for consistency
- Test incrementally with simple cases
- Keep protocol constants accurate to spec