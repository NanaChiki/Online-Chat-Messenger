# Stage 2 Specification

## Overview
**Recommended Language**: Python (both server and client)

This stage creates a chat messenger system where clients can host their own chat rooms and invite others to join. Clients interact with the server through CLI, with the ability to create new chat rooms or join existing ones by name. Chat rooms may be password-protected.

## Architecture
The system uses a dual-protocol approach:
1. **TCP**: Initial connection for room creation/joining and token generation
2. **UDP**: Real-time chat messaging within rooms

## Protocol Specifications

### TCP - Chat Room Protocol (TCRP)

#### Message Structure
- **Header** (32 bytes):
  - `RoomNameSize` (1 byte): Size of room name (max 28 bytes)
  - `Operation` (1 byte): Operation code
  - `State` (1 byte): Transaction state
  - `OperationPayloadSize` (29 bytes): Size of operation payload (max 2^29 bytes)
- **Body**: 
  - First `RoomNameSize` bytes: Room name (UTF-8 encoded)
  - Next `OperationPayloadSize` bytes: Operation payload

#### Operations

##### Room Creation (Operation Code: 1)
1. **Server Initialization (State: 0)**
   - Client sends room creation request
   - Payload: Desired username
2. **Response to Request (State: 1)**
   - Server responds with status code
3. **Request Completion (State: 2)**
   - Server sends unique token (up to 255 bytes)
   - Token identifies client as room host
   - TCP connection terminated

##### Room Joining (Operation Code: 2)
- Same state flow as room creation
- Client receives token but is not designated as host
- TCP connection terminated after token delivery

#### Token Management
- Server maintains list of permitted tokens per chat room
- Token must match client IP address for message relay
- Host token has special privileges (room closure authority)

### UDP - Chat Messaging

#### Client to Server Packet
- **Maximum Size**: 4096 bytes
- **Header**:
  - `RoomNameSize` (1 byte)
  - `TokenSize` (1 byte)
- **Body**:
  - Room name (`RoomNameSize` bytes)
  - Token (`TokenSize` bytes)
  - Message (remaining bytes)

#### Server to Client Packet
- **Maximum Size**: 4094 bytes
- **Content**: Message only (no headers)

## Functional Requirements

### Room Management
- Clients can create new chat rooms via TCP
- Clients can join existing rooms by name
- Password protection support for rooms
- Room remains active while host is present
- Room automatically closes when host leaves

### Authentication & Authorization
- Unique token generation per client
- Token-IP address binding for security
- Token validation for all UDP communications
- Automatic token cleanup on client disconnect

### Messaging
- Real-time UDP-based messaging
- Message relay to all room participants
- Disconnect notifications
- Rejoin capability after disconnection
- Same chat requirements as Stage 1

## Non-Functional Requirements

### Performance
- Support minimum 10,000 packets per second
- Scale to 500 concurrent chat rooms
- Handle 10 users per room sending 2 messages/second average

### Reliability
- Prioritize real-time delivery over guaranteed delivery
- Automatic reconnection handling
- Graceful degradation on network issues

## Implementation Notes
- UTF-8 encoding for room names
- JSON/string/integer encoding for operation payloads based on context
- Automatic UDP connection after TCP handshake
- Token-based security model throughout system