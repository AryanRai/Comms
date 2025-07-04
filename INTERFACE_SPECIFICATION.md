# AriesUI ↔ Comms Interface Specification

## Overview

This document defines the standardized interface between AriesUI and your existing Comms infrastructure, specifically how AriesUI connects to your StreamHandler and Engine components.

## Architecture Overview

```
┌─────────────────┐    WebSocket     ┌─────────────────┐    Python API    ┌─────────────────┐
│    AriesUI      │◄────────────────►│  StreamHandler  │◄─────────────────►│     Engine      │
│   (Frontend)    │   Port 3000      │      (sh)       │                   │      (en)       │
│                 │                  │                 │                   │                 │
│ - Next.js/React │                  │ - Socketify     │                   │ - DynamicModules│
│ - TypeScript    │                  │ - 100ms timeout │                   │ - 100ms updates │
└─────────────────┘                  └─────────────────┘                   └─────────────────┘
                                            ▲
                                            │
                                            │
                                    ┌───────┴───────┐
                                    │ HyperThreader │
                                    │   Process     │
                                    │   Manager     │
                                    └───────────────┘
```

## 1. Communication Protocol

### 1.1 WebSocket Connection
- **Endpoint**: `ws://localhost:3000`
- **Protocol**: WebSocket with JSON messages
- **Timeout**: 100ms idle timeout
- **Update Rate**: 100ms for both Engine and StreamHandler

### 1.2 Message Format

All messages follow this structure:

```typescript
interface CommsMessage {
  type: 'negotiation' | 'control' | 'control_response' | 'config_update' | 'config_response'
  status: 'active' | 'inactive' | 'error' | 'forwarded'
  data: { [moduleId: string]: any }
  'msg-sent-timestamp': string  // Format: YYYY-MM-DD HH:MM:SS
}
```

## 2. Data Structures

### 2.1 Module Definition
```typescript
interface CommsModule {
  module_id: string
  name: string
  status: 'active' | 'inactive' | 'error'
  'module-update-timestamp': string
  config: {
    update_rate: number
    enabled_streams: string[]
    debug_mode: boolean
    [key: string]: any
  }
  streams: { [streamId: string]: CommsStream }
}
```

### 2.2 Stream Definition
```typescript
interface CommsStream {
  stream_id: number
  name: string
  datatype: string
  unit?: string
  status: 'active' | 'inactive' | 'error'
  metadata: {
    sensor?: string
    precision?: number
    location?: string
    [key: string]: any
  }
  value: any
  'stream-update-timestamp': string
  priority: 'high' | 'medium' | 'low'
}
```

## 3. Message Types & Flows

### 3.1 Module Data Updates (Engine → StreamHandler → AriesUI)
```json
{
  "type": "negotiation",
  "status": "active",
  "data": {
    "hw_module_1": {
      "module_id": "hw_module_1",
      "name": "Hardware Module 1",
      "status": "active",
      "module-update-timestamp": "2024-03-14 12:00:00",
      "config": {
        "update_rate": 0.1,
        "enabled_streams": ["1"],
        "debug_mode": false
      },
      "streams": {
        "1": {
          "stream_id": 1,
          "name": "Temperature",
          "datatype": "float",
          "unit": "°C",
          "status": "active",
          "metadata": {
            "sensor": "TMP36",
            "precision": 0.1,
            "location": "main"
          },
          "value": 25.4,
          "stream-update-timestamp": "2024-03-14 12:00:00",
          "priority": "high"
        }
      }
    }
  },
  "msg-sent-timestamp": "2024-03-14 12:00:00"
}
```

### 3.2 Control Commands (AriesUI → StreamHandler → Engine)
```json
{
  "type": "control",
  "status": "active",
  "data": {
    "module_id": "hw_module_1",
    "command": {
      "stream_id": "1",
      "value": 26.0
    }
  },
  "msg-sent-timestamp": "2024-03-14 12:00:01"
}
```

### 3.3 Control Response (StreamHandler → AriesUI)
```json
{
  "type": "control_response",
  "module_id": "hw_module_1",
  "status": "forwarded"
}
```

### 3.4 Configuration Updates (AriesUI → StreamHandler → Engine)
```json
{
  "type": "config_update",
  "status": "active",
  "data": {
    "module_id": "hw_module_1",
    "config": {
      "update_rate": 0.2,
      "enabled_streams": ["1", "2"],
      "debug_mode": true
    }
  },
  "msg-sent-timestamp": "2024-03-14 12:00:02"
}
```

### 3.5 Configuration Response (StreamHandler → AriesUI)
```json
{
  "type": "config_response",
  "module_id": "hw_module_1",
  "status": "forwarded"
}
```

## 4. Implementation Requirements

### 4.1 StreamHandler Configuration
- WebSocket idle timeout: 100ms
- Message forwarding to all subscribed clients
- Debug window for monitoring messages
- Configuration window for runtime settings

### 4.2 Engine Configuration
- Update rate: 100ms
- Dynamic module loading from DynamicModules directory
- Automatic module initialization and cleanup
- Debug window for monitoring module state

### 4.3 AriesUI Requirements
- Auto-reconnection to StreamHandler
- Real-time stream value updates
- Module configuration interface
- Error handling and status display

## 5. Development Tools

### 5.1 Debug Windows
Both StreamHandler and Engine provide debug windows showing:
- Active modules and streams
- Real-time values
- Connection status
- Message flow

### 5.2 Configuration Windows
Both components provide configuration windows for:
- Update rates
- Debug levels
- Connection settings
- Module-specific settings

## 6. Error Handling

### 6.1 Connection Errors
- Auto-reconnection with 5-second delay
- Connection status propagation
- Error logging in debug windows

### 6.2 Message Errors
- JSON parse error handling
- Invalid message type handling
- Module not found handling

## 7. Performance Considerations

### 7.1 Update Rates
- Engine update rate: 100ms
- StreamHandler timeout: 100ms
- UI refresh rate: Configurable, default 100ms

### 7.2 Message Size
- Keep messages compact
- Only send changed values
- Use appropriate data types

## 8. Security Notes

### 8.1 Network
- WebSocket runs on localhost only
- No authentication (internal use)
- No encryption (internal use)

### 8.2 Module Loading
- Only load modules from DynamicModules directory
- Validate module structure before initialization
- Safe cleanup on module errors

This specification matches your existing implementation while providing a clear interface for AriesUI integration. 