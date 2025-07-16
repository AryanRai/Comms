# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Comms v3.0 is a high-performance, modular communications platform for hardware development, real-time monitoring, and data acquisition systems. It consists of a Python backend engine with WebSocket streaming and a modern React-based dashboard (AriesUI) for visualization and control.

## Essential Commands

### Development Workflow

**Start the complete system (recommended):**
```bash
python HyperThreader.py
```

**Manual component startup:**
```bash
# Terminal 1: Stream Handler (WebSocket server)
cd sh && python sh.py

# Terminal 2: Hardware Engine (device interface)
cd en && python en.py

# Terminal 3: AriesUI Desktop App
cd ui/ariesUI && npm run electron-dev

# OR AriesUI Web Version
cd ui/ariesUI && npm run dev
```

### Frontend Development (AriesUI)

**Install dependencies:**
```bash
cd ui/ariesUI && npm install
```

**Development commands:**
```bash
npm run dev              # Next.js development server
npm run electron-dev     # Electron + Next.js development
npm run build           # Production web build
npm run build-electron  # Production desktop build
npm run lint           # Code linting
```

### Backend Development

**Python dependencies:**
```bash
pip install socketify labjack-ljm numpy pandas pywebview bottle
```

**Run individual components:**
```bash
# Stream Handler
cd sh && python stream_handlerv3.0_physics.py

# Hardware Engine (latest version)
cd en && python enginev0.6.py
```

## Architecture Overview

### Core System Structure

**Backend Components (Python):**
- **HyperThreader.py**: Process manager with GUI for starting/stopping all components
- **sh/ (Stream Handler)**: WebSocket server for real-time bidirectional communication
- **en/ (Engine)**: Hardware interfacing with dynamic module loading system
- **en/DynamicModules/**: Hardware wrappers for sensors, actuators, and devices

**Frontend Components (React/Next.js):**
- **ui/ariesUI/**: High-performance dashboard with 60fps rendering
- **components/main-content/**: Modular main content system (refactored from 2,719 lines to ~400)
- **components/grid/**: Virtual grid system with viewport culling
- **ariesMods/**: Extensible plugin system for custom widgets
- **electron/**: Cross-platform desktop application support

### Communication Protocol

**WebSocket Message Format:**
```json
{
  "type": "negotiation",
  "status": "active",
  "data": {
    "module_id": {
      "name": "Module Name",
      "status": "active",
      "streams": {
        "stream_id": {
          "stream_id": 1,
          "name": "Stream Name",
          "datatype": "float",
          "unit": "unit",
          "value": 123.45,
          "status": "active"
        }
      }
    }
  },
  "msg-sent-timestamp": "2024-10-30 00:09:54"
}
```

### Hardware Integration

**Dynamic Module System:**
- Modules located in `en/DynamicModules/`
- Each module implements standardized Stream and Module classes
- Real-time hardware interfacing with configurable update rates (10ms-10s)
- Support for Serial, LabJack, and custom hardware interfaces

**Creating Hardware Modules:**
```python
# en/DynamicModules/my_module.py
class MyModule:
    def __init__(self):
        self.config = {"update_rate": 0.1}
        self.streams = {
            "1": Stream(stream_id=1, name="Sensor", datatype="float", unit="V", status="active")
        }
    
    async def update_streams_forever(self):
        while True:
            self.streams["1"].update_value(self.read_hardware())
            await asyncio.sleep(self.config["update_rate"])
```

## AriesMods Plugin System

**Plugin Categories:**
- **sensors/**: Hardware sensor widgets
- **controls/**: Interactive control widgets (toggles, sliders, buttons)
- **visualization/**: Charts, graphs, and data visualization
- **utility/**: Utility widgets (clock, diagnostics, data tables)
- **templates/**: Development templates for new widgets

**Creating Custom AriesMods:**
```typescript
// ariesMods/sensors/CustomSensor.tsx
import { AriesModProps } from '@/types/ariesmods'
import { useCommsStream } from '@/hooks/use-comms-stream'

const CustomSensor: React.FC<AriesModProps> = ({ title, config }) => {
  const { value, status } = useCommsStream(config.streamId)
  
  return (
    <div className="widget-container">
      <h3>{title}</h3>
      <div className="value">{value} {config.unit}</div>
    </div>
  )
}
```

## Performance Features

**Key Optimizations:**
- **60fps Rendering**: Hardware-accelerated transforms with RequestAnimationFrame
- **Virtual Grid**: Only visible widgets rendered (up to 75% culling efficiency)
- **Memory Optimization**: 50% reduction in memory usage from v2.0
- **Stream Latency**: <10ms for local hardware connections
- **Widget Capacity**: 100+ widgets with smooth interactions

## Project Structure

```
Comms/
├── HyperThreader.py              # Process manager
├── sh/                           # Stream Handler
│   ├── sh.py                    # WebSocket server
│   └── stream_handlerv3.0_physics.py  # Latest version
├── en/                          # Hardware Engine
│   ├── en.py                   # Main engine
│   ├── enginev0.6.py           # Latest version
│   └── DynamicModules/         # Hardware modules
├── ui/ariesUI/                 # AriesUI Dashboard
│   ├── components/             # React components
│   │   ├── main-content/      # Modular main content
│   │   ├── grid/              # Grid system
│   │   └── widgets/           # Widget system
│   ├── ariesMods/             # Plugin system
│   ├── hooks/                 # Custom React hooks
│   └── electron/              # Desktop app
├── int/StarSim/               # StarSim physics integration
│   └── ParsecCore/            # C++ physics engine
└── Public/AriesMods/          # Plugin configurations
```

## Development Notes

**Testing:**
- No specific test framework configured - check individual component READMEs
- Use `HyperThreader.py` for integrated testing of all components
- Hardware modules can be tested individually through the engine

**Git Submodules:**
- AriesUI is included as a git submodule in `ui/ariesUI`
- Use `git submodule update --init --recursive` after cloning
- See CONTRIBUTE.md for detailed submodule workflow

**StarSim Integration:**
- C++ physics engine located in `int/StarSim/ParsecCore/`
- Uses CMake build system with GoogleTest
- See `int/StarSim/CLAUDE.md` for detailed build instructions

## Key Configuration Files

- **package.json**: Frontend dependencies and build scripts
- **requirements.txt**: Python dependencies
- **Public/AriesMods/mods.json**: Plugin configurations
- **ui/ariesUI/tsconfig.json**: TypeScript configuration
- **ui/ariesUI/components.json**: Shadcn/ui component configuration