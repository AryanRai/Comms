# AriesUI ↔ Comms Implementation Guide

## Overview

This guide provides step-by-step instructions for connecting AriesUI to your existing Comms WebSocket infrastructure. We'll create TypeScript/React components that integrate with your StreamHandler and Engine's existing WebSocket implementation.

## Quick Reference

**What you'll build:**
- TypeScript interfaces matching your existing message format
- React hooks for WebSocket communication
- Real-time data streaming components
- Hardware control widgets
- Auto-reconnection handling

**Development time:** 2-3 days for basic integration

## Running the System

### Option 1: Using HyperThreader (Recommended)

HyperThreader provides a unified interface to manage all Comms components:

1. Start HyperThreader:
```bash
python HyperThreader.py
```

2. Use the GUI to:
   - Start/Stop StreamHandler
   - Start/Stop Engine
   - Start/Stop AriesUI in development mode
   - Build AriesUI for production
   - Monitor performance metrics
   - Configure update rates
   - View debug information

### Option 2: Manual Component Start

If you prefer to start components manually:

```bash
# Start Stream Handler
cd sh
python sh.py

# Start Engine
cd en
python en.py

# Start AriesUI in development mode
cd ui/ariesUI
npm run electron-dev

# OR build and run AriesUI in production
npm run build-electron
```

## Phase 1: TypeScript Interface Definition

### 1.1 Create Type Definitions

Create `ui/ariesUI/types/comms.ts`:

```typescript
// Message types matching your existing StreamHandler format
export interface CommsMessage {
  type: 'negotiation' | 'control' | 'control_response' | 'config_update' | 'config_response'
  status: 'active' | 'inactive' | 'error' | 'forwarded'
  data: { [moduleId: string]: any }
  'msg-sent-timestamp': string
}

// Module structure matching your Engine's format
export interface CommsModule {
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

// Stream structure matching your Engine's Stream class
export interface CommsStream {
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

## Phase 2: WebSocket Client Hook

### 2.1 Create WebSocket Hook

Create `ui/ariesUI/hooks/use-comms-socket.ts`:

```typescript
import { useState, useEffect, useCallback } from 'react'
import { CommsMessage, CommsModule } from '@/types/comms'

export function useCommsSocket(url: string = 'ws://localhost:8000') {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [modules, setModules] = useState<Map<string, CommsModule>>(new Map())
  const [lastMessage, setLastMessage] = useState<CommsMessage | null>(null)

  // Connect to WebSocket
  useEffect(() => {
    const ws = new WebSocket(url)

    ws.onopen = () => {
      console.log('Connected to StreamHandler')
      setIsConnected(true)
    }

    ws.onclose = () => {
      console.log('Disconnected from StreamHandler')
      setIsConnected(false)
      // Attempt reconnection after 5 seconds
      setTimeout(() => setSocket(new WebSocket(url)), 5000)
    }

    ws.onmessage = (event) => {
      try {
        const message: CommsMessage = JSON.parse(event.data)
        setLastMessage(message)

        // Handle negotiation messages (module updates)
        if (message.type === 'negotiation') {
          const newModules = new Map(modules)
          Object.entries(message.data).forEach(([moduleId, moduleData]) => {
            newModules.set(moduleId, moduleData as CommsModule)
          })
          setModules(newModules)
        }
      } catch (error) {
        console.error('Failed to parse message:', error)
      }
    }

    setSocket(ws)
    return () => ws.close()
  }, [url])

  // Send control command
  const sendCommand = useCallback((moduleId: string, command: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      const message: CommsMessage = {
        type: 'control',
        status: 'active',
        data: {
          module_id: moduleId,
          command: command
        },
        'msg-sent-timestamp': new Date().toISOString()
      }
      socket.send(JSON.stringify(message))
    }
  }, [socket])

  // Update module configuration
  const updateConfig = useCallback((moduleId: string, config: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      const message: CommsMessage = {
        type: 'config_update',
        status: 'active',
        data: {
          module_id: moduleId,
          config: config
        },
        'msg-sent-timestamp': new Date().toISOString()
      }
      socket.send(JSON.stringify(message))
    }
  }, [socket])

  return {
    isConnected,
    modules,
    lastMessage,
    sendCommand,
    updateConfig
  }
}
```

## Phase 3: React Components

### 3.1 Create Module Display Component

Create `ui/ariesUI/components/hardware/module-display.tsx`:

```typescript
import { useCommsSocket } from '@/hooks/use-comms-socket'
import { Badge } from '@/components/ui/badge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

export function ModuleDisplay() {
  const { isConnected, modules } = useCommsSocket()

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Hardware Modules</h2>
        <Badge variant={isConnected ? "default" : "destructive"}>
          {isConnected ? "Connected" : "Disconnected"}
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Array.from(modules.values()).map(module => (
          <Card key={module.module_id}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{module.name}</span>
                <Badge variant={module.status === 'active' ? "default" : "secondary"}>
                  {module.status}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(module.streams).map(([streamId, stream]) => (
                  <div key={streamId} className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">{stream.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {stream.datatype} • {stream.unit || 'no unit'}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono">
                        {stream.value} {stream.unit}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(stream['stream-update-timestamp']).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
```

### 3.2 Create Control Widget

Create `ui/ariesUI/components/hardware/control-widget.tsx`:

```typescript
import { useState } from 'react'
import { useCommsSocket } from '@/hooks/use-comms-socket'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

interface ControlWidgetProps {
  moduleId: string
  streamId: string
}

export function ControlWidget({ moduleId, streamId }: ControlWidgetProps) {
  const { modules, sendCommand } = useCommsSocket()
  const [value, setValue] = useState('')

  const module = modules.get(moduleId)
  const stream = module?.streams[streamId]

  const handleSend = () => {
    sendCommand(moduleId, {
      stream_id: streamId,
      value: value
    })
  }

  if (!stream) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle>{stream.name} Control</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex space-x-2">
          <Input
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={`Enter ${stream.datatype} value`}
          />
          <Button onClick={handleSend}>Send</Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

## Phase 4: Integration

### 4.1 Update App Page

Update `ui/ariesUI/app/page.tsx`:

```typescript
import { ModuleDisplay } from '@/components/hardware/module-display'

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <ModuleDisplay />
    </main>
  )
}
```

### 4.2 Test Integration

1. Start your existing backend:
```bash
# Terminal 1: Start StreamHandler
python sh/sh.py

# Terminal 2: Start Engine
python en/en.py
```

2. Start AriesUI:
```bash
# Terminal 3: Start frontend
cd ui/ariesUI
npm run dev
```

3. Open `http://localhost:3000` to see your hardware modules and streams

## Next Steps

1. Add more specialized widgets for different stream types
2. Implement configuration interface
3. Add error handling and reconnection UI
4. Create debug view for message inspection
5. Add stream history visualization

This implementation works directly with your existing WebSocket infrastructure in StreamHandler and Engine, requiring no changes to your Python backend. 