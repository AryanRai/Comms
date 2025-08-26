# Contributing Guide

Welcome to Comms Alpha v3.0! This guide will help you contribute to the project, whether you're working on hardware modules, AriesMods widgets, or the core system.

## 🚀 Quick Setup

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **Git** with submodule support
- **C++ Compiler** (for StarSim integration)

### Initial Setup
```bash
# Clone with all submodules
git clone --recursive https://github.com/AryanRai/Comms.git
cd Comms

# Install Python dependencies
pip install socketify labjack-ljm numpy pandas pywebview bottle

# Install UI dependencies
cd ui/ariesUI
npm install
cd ../..

# Test the setup
python HyperThreader.py
```

## 🏗️ Project Architecture

Understanding the project structure will help you contribute effectively:

```
Comms/
├── 🐍 Backend (Python)
│   ├── sh/stream_handlerv3.0_physics.py  # Unified Protocol WebSocket Server
│   ├── en/enginev0.6.py                  # Hardware Engine
│   └── HyperThreader.py                  # Process Manager
├── ⚛️ Frontend (React/TypeScript)
│   └── ui/ariesUI/                       # AriesUI Dashboard
├── 🔬 Physics Integration
│   └── int/StarSim/                      # StarSim Physics Engine
└── 📚 Documentation
    └── int/chyappy/UNIFIED_PROTOCOL_V3.md # Protocol Documentation
```

## 🧩 Working with AriesMods

AriesMods are the plugin system for AriesUI. All physics widgets now use the **Unified Protocol v3.0**.

### Creating a New AriesMod
```typescript
// ui/ariesUI/ariesMods/sensors/MyCustomSensor.tsx
import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useCommsStream } from '@/hooks/use-comms-stream'
import type { AriesModProps } from '@/types/ariesmods'

const MyCustomSensor: React.FC<AriesModProps> = ({ title, config }) => {
  // Use unified protocol for real-time data
  const { data, isConnected } = useCommsStream(config.streamId)
  
  return (
    <Card className="w-full h-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {data?.value ?? '--'} {config.unit}
        </div>
        <div className="text-sm text-muted-foreground">
          Status: {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </CardContent>
    </Card>
  )
}

export default MyCustomSensor
```

## 🔌 Working with Hardware Modules

Hardware modules connect physical devices to the Comms ecosystem.

### Creating a Hardware Module
```python
# en/DynamicModules/my_hardware_module.py
import asyncio
from datetime import datetime

class MyHardwareModule:
    def __init__(self):
        self.name = "My Hardware Module"
        self.version = "1.0.0"
        self.description = "Custom hardware interface"
        
        # Configure streams using unified format
        self.streams = {
            "sensor_1": {
                "stream_id": "sensor_1",
                "name": "Temperature Sensor",
                "datatype": "float",
                "unit": "°C",
                "value": 0.0,
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        self.config = {
            'update_rate': 0.1,  # 100ms updates
            'enabled_streams': ['sensor_1'],
            'debug_mode': False
        }
    
    async def update_streams_forever(self):
        """Main loop for updating stream data"""
        while True:
            # Read from your hardware here
            temperature = self.read_temperature_sensor()
            
            # Update stream data
            self.streams["sensor_1"]["value"] = temperature
            self.streams["sensor_1"]["timestamp"] = datetime.now().isoformat()
            
            await asyncio.sleep(self.config['update_rate'])
    
    def read_temperature_sensor(self):
        # Implement your hardware reading logic
        return 25.0  # Example temperature
```

## 🔬 Working with StarSim Integration

StarSim integration uses the **Unified Protocol v3.0** for seamless communication.

### Physics Simulation Integration
```cpp
// Example C++ integration with InputManager
#include "parsec/InputManager.h"

int main() {
    // Create input manager for physics simulation
    parsec::InputManager input_manager("my_simulation");
    
    // Connect to unified stream handler
    input_manager.initialize("ws://localhost:3000");
    
    // Register physics streams
    input_manager.registerStream("position", "Position", "float", "m");
    input_manager.registerStream("velocity", "Velocity", "float", "m/s");
    
    // Simulation loop
    for (int i = 0; i < 1000; ++i) {
        // Update physics
        double position = calculate_position();
        double velocity = calculate_velocity();
        
        // Send to AriesUI via unified protocol
        input_manager.updateStreamValue("position", position);
        input_manager.updateStreamValue("velocity", velocity);
        
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    
    return 0;
}
```

## 🌐 Working with the Unified Protocol

The **Unified Protocol v3.0** combines Chyappy, WebSocket, and Physics protocols.

### Message Format
```json
{
  "type": "negotiation",
  "status": "active",
  "data": {
    "stream_id": {
      "stream_id": "simulation_position",
      "name": "Physics Position",
      "datatype": "float",
      "unit": "m",
      "value": 1.23,
      "status": "active",
      "timestamp": "2025-07-19T20:25:35.123Z",
      "simulation_id": "spring_mass_system"
    }
  },
  "msg-sent-timestamp": "2025-07-19 20:25:35"
}
```

### WebSocket Connection
```typescript
// AriesUI automatically connects using CommsStreamClient
import { commsClient } from '@/lib/comms-stream-client'

// Subscribe to streams
commsClient.subscribeToStream('simulation_position', (value, metadata) => {
  console.log('Position:', value, metadata.unit)
})

// Send physics commands
commsClient.sendPhysicsCommand('spring_mass_system', 'start', {})
```

## 🔧 Working with Submodules

This project includes AriesUI and StarSim as git submodules.

### Initial Setup
When first cloning the repository, you'll need to initialize the submodule:
```bash
git clone <repository-url>
git submodule update --init --recursive
```

### Making Changes to AriesUI

#### If you have write access to AriesUI:
1. Navigate to the submodule directory:
   ```bash
   cd ui/ariesUI
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

3. Return to the parent repository and update the submodule reference:
   ```bash
   cd ../..
   git add ui/ariesUI
   git commit -m "Updated ariesUI submodule"
   git push
   ```

#### If you don't have write access to AriesUI:
1. Fork the [AriesUI repository](https://github.com/AryanRai/AriesUI) to your GitHub account
2. Update the submodule to point to your fork:
   ```bash
   git submodule set-url ui/ariesUI https://github.com/YOUR_USERNAME/AriesUI.git
   ```
3. Then follow the same steps as above to make changes

### Updating AriesUI
To update the submodule to its latest version:
```bash
git submodule update --remote ui/ariesUI
git add ui/ariesUI
git commit -m "Updated ariesUI submodule to latest version"
git push
```

### Important Notes
- Always commit and push changes in the submodule first, before committing in the parent repository
- Make sure you have the necessary permissions before pushing to the original AriesUI repository
- If you're working on a branch, make sure to create branches in both the main repository and the submodule 