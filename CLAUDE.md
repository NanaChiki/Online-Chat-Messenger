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
  - Protocol constants and enums (tcp_protocol.py lines 1-68)
  - Message classes and status codes

### 🚧 In Progress
- **tcp_protocol.py**: ~50% complete
  - ✅ Constants, enums, TCRPMessage class
  - ⏳ TODO: encode/decode functions, helper functions, TokenManager class

### 📅 Next Steps
1. Complete tcp_protocol.py implementation
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
- **Max Room Name**: 28 bytes
- **Max Payload**: 2^29 bytes  
- **Token Size**: Up to 255 bytes
- **Operations**: CREATE_ROOM (1), JOIN_ROOM (2)
- **States**: REQUEST (0), RESPONSE (1), COMPLETION (2)

### Current Protocol Constants Issues
❌ **Found Issues** (need fixing):
- `MAX_OPERATION_PAYLOAD_SIZE = 32` should be `(2**29) - 1`
- Comments inconsistent with spec

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
1. **Continue Stage 2**: Focus on tcp_protocol.py completion
2. **Protocol Debugging**: Compare constants with specification
3. **Testing**: Create test cases for new implementations
4. **Git Management**: Concise commits, push to origin/master

## 💡 Development Tips
- Check specification first before implementing
- Use existing Stage 1 patterns for consistency
- Test incrementally with simple cases
- Keep protocol constants accurate to spec