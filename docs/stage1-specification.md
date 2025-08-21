# Stage 1 Specification

## Protocol Overview

- Transport: UDP
- Maximum Message Size: 4096 bytes
- Character encoding: UTF-8

## Message Format

```
[username_len(1byte)][username (variable)][message(variable)]
```

## Implementation Requirements

- Server maintains client list in memory
- Messages broadcasted to all connected clients
- Client timeout mechanism for connection cleanup
- Real-time message delivery priority over reliability
