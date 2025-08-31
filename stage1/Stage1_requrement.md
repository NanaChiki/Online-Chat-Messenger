# Stage 1 Requirements

### Functional requirements

The server is started via CLI and waits for incoming connections in the background. If the server is offline, it means the chat service itself is stopped.

- [] The server and client exchange messages using UDP network sockets.
- [] When sending messages, the server and client process messages up to 4096 bytes at a time. This is the maximum size of messages that the client can send. Similarly, messages of up to 4096 bytes are forwarded to all other clients.
- [] When a session starts, the client prompts the user to enter a username.
- [] The message transmission protocol is relatively simple. The first byte of the message, usernamelen, indicates the total byte size of the username, which can be up to 255 characters (2^8 - 1 bytes). The server reads this initial usernamelen byte to identify the sender's username. The subsequent bytes are the actual message being sent. This information can be freely used by the server and client, allowing for display or storage of the username.
- [] Byte data is encoded and decoded in UTF-8. This means that one character is represented by 1 to 4 bytes. Python's str.encode and str.decode methods have this behavior by default.
- [] The server has a relay system built in, which temporarily stores information of all currently connected clients in memory. When a new message arrives at the server, that message is relayed to all currently connected clients.
- [] If the client fails several times in a row or has not sent a message for a while, they will be automatically removed from the relay system. Unlike TCP in this regard, UDP is connectionless, so it is necessary to track the last message transmission time for each client.

### Non-functional requirements

- [] The chat messaging system is considered to prioritize real-time data over reliable data.
- [] The system must support the transmission of at least 10,000 packets per second. For example, if 1,000 people are in a single chat room, the system should be designed to process at least 10 messages per second. Typical hardware can meet this condition.
