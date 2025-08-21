# Online Chat Messenger

A multi-stage online chat messenger application built to demonstrate client-server architecture and network programming concepts.

## 🎯 Project Overview

This project demonstrates a real-time chat messaging service in three progressive stages:

### Stage 1: Basic UDP Chat

- Simple UDP-based client-server communication
- CLI clients connect to server
- Messages are broadcasted to all connected clients
- Maximum message size: 4096 bytes (4KB)
- UTF-8 encoding for all text data

### Stage 2: Chat Rooms

- TCP connection for room creation and joining
- Custom TCP Chat Room Protocol (TCRP)
- Room-based messaging with host permissions
- Client authentication using tokens
- UDP messaging within rooms

### Stage 3: Advanced Features (Optional)

- Password-protected chat rooms
- Desktop GUI client (Electron.js)
- Message encryption (RSA-like)
- Scalability considerations

## 🛠 Technology Stack

- **Backend**: Python
- **Protocol**: TCP/UDP custom protocols
- **CLI Client**: Python
- **GUI Client**: Electron.js (JavaScript/TypeScript)
- **Encoding**: UTF-8

## 📁 Project Structure

```text
Online-Chat-Messenger/
├── docs/ # Design documents
├── stage1/ # Stage 1 implementation
├── stage2/ # Stage 2 implementation

├── stage3/ # Stage 3 implementation
├── tests/ # Test files
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js (for Stage 3 GUI client)

### Running Stage 1

```bash
cd stage1
python server.py
```

In another terminal:

```bash
cd stage1
python client.py
```

## 📈 Learning Objectives

This project focuses on:

- Client-server architecture understanding
- Network programming (TCP/UDP)
- Protocol design and implementation
- Real-time data processing
- Scalability considerations

## 🎓 Skills Developed

- Backend development
- Computer networking
- Operating systems
- System programming
- Protocol design

## 📝 License

This project is for educational purposes.
