# Comms Alpha v3.0 (Dev Branch)

![Comms3.0](https://github.com/user-attachments/assets/02e70432-e6f7-4664-9f17-b6b0acd60a67)  
**A centralized communications dashboard for multi-layered control in ground stations, all-in-one DAQ solutions, and hardware interfaces.**  
Comms is a modular, extensible platform designed to streamline hardware development and monitoring.

[![Version](https://img.shields.io/badge/Version-Alpha%20v3.0-blue)](https://github.com/AryanRai/Comms/tree/Dev3.0V) [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE) [![Contact](https://img.shields.io/badge/Email-aryanrai170@gmail.com-orange)](mailto:aryanrai170@gmail.com)

---

## Project Overview

### Versions
- **Alpha v1.0**: First stable release with one-way communication.
- **Alpha v2.0**: Added two-way communication and performance boosts.
- **Alpha v3.0 (Current)**: Complete UI rebuild with AriesUI, enhanced hardware integration.

### Core Components
1. **Engine + Dynamic Modules (Python)** - Hardware interfacing and data streams.
2. **Stream Handler + Stream Transformers (Python + WebSocket)** - Real-time data flow.
3. **AriesUI (Next.js + Electron + TailwindCSS)** - Modern, responsive UI with hardware integration.
4. **HyperThreader** - Process management and monitoring.

---

## What's New in v3.0?

<details>
<summary><b>Click to Explore v3.0 Features</b></summary>

### AriesUI Rebuild
- Complete UI rebuild using Next.js and Electron
- Real-time hardware monitoring with WebSocket integration
- Drag-and-drop widget system with collision detection
- Dark/light theme support
- Desktop application support

### Enhanced Hardware Integration
- Improved two-way communication
- Real-time hardware status monitoring
- Advanced widget system for hardware control
- Configurable update rates via HyperThreader

### Process Management
- HyperThreader GUI for process control
- Real-time performance monitoring
- Configurable update rates
- Debug windows for all components

</details>

---

## Quick Start

### Option 1: Using HyperThreader (Recommended)
```bash
# Clone v3.0 Dev Branch
git clone -b Dev3.0V https://github.com/AryanRai/Comms.git
cd Comms

# Install Python dependencies
pip install socketify

# Install UI dependencies
cd ui/ariesUI
npm install
cd ../..

# Start HyperThreader
python HyperThreader.py
```

Use the HyperThreader GUI to:
- Start/Stop StreamHandler
- Start/Stop Engine
- Start/Stop AriesUI
- Monitor performance
- Configure update rates
- View debug information

### Option 2: Manual Component Start
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

---

## System Architecture

<details>
<summary><b>Engine (aka "en")</b></summary>

- **Role**: Core layer for hardware communications.
- **Features**:
  - Dynamic module loading with safe initialization.
  - Async operations and hardware abstraction.
  - Configurable update rates (100ms default in v2.0).
  - Error handling, recovery, and debug propagation.
  - Value change notifications (v2.0).
- **DynamicModules (DynMods)**:
  - Hardware wrappers (e.g., sensors) using serial or other methods.
  - Streams hardware variables to the Engine.
  - Examples: Serial Communication, Random Number Generator, Custom Templates.
  - **Negotiator Class**: Links Engine to Stream Handler.

</details>

<details>
<summary><b>Stream Handler (aka "sh")</b></summary>

- **Role**: Manages data flow between Engine and UI.
- **Features**:
  - WebSocket-based (Socketify, 100ms timeout in v2.0).
  - Message queuing, priority routing, and compression.
  - Real-time stream creation/deletion/updates.
  - Debug interface with pause/resume (v2.0).
- **Streams**:
  - Syncs data exchanges (actions, readings) between frontend/backend.
  - One-sided or bidirectional (v2.0).
- **Logger**: Logs active readings and actions.
- **Stream Transformer**: Applies protocol/message conversions.

</details>

<details>
<summary><b>AriesUI (aka "ui")</b></summary>

- **Role**: Visualization and control interface.
- **Features**:
  - Grid layout (Gridstack) with drag-and-drop widgets.
  - Real-time data visualization and monitoring.
  - New widgets: Toggle, Slider, Value Monitor (v2.0).
  - Responsive to rate changes with error feedback (v2.0).
- **AriesMods**:
  - Extensions: JavaScript, UI, Backend Hardware, or combinations.
  - **Marketplace**: Centralized module hub.
- **Profiles**: Stores layouts, streams, and hardware configs (saved locally).

</details>

---

## Core Features

<details>
<summary><b>Alpha v1.0 (Implemented)</b></summary>

- One-way communication, data acquisition, and visualization.
- Engine with custom plugins and DynamicModules.
- Stream Handler with WebSocket streaming.
- AriesUI with dynamic dashboards.
- AriesMods: Drag-and-drop widgets, live data, marketplace.
- HyperThreader for instance management.

</details>

<details>
<summary><b>Alpha v2.0 (New Features)</b></summary>

- Two-way communication with real-time control.
- Enhanced stream management (metadata, priorities).
- New widgets: Toggle, Slider, Value Monitor.
- Performance: 100ms update rate, HyperThreader-configurable.
- Debug: Logging, history, real-time status.

</details>

---

## Stream Format

### Standard Message (v1.0 & v2.0)
```json
{
  "type": "negotiation",
  "status": "active",
  "data": {
    "module_id": {
      "name": "Module Name",
      "status": "active",
      "config": {
        "update_rate": 1.0,
        "enabled_streams": ["stream1"],
        "debug_mode": false
      },
      "streams": {
        "stream1": {
          "stream_id": 1,
          "name": "Temperature",
          "datatype": "float",
          "unit": "Celsius",
          "status": "active",
          "metadata": {
            "sensor": "TMP36",
            "precision": 0.1,
            "location": "main_chamber"
          },
          "value": 25.4,
          "priority": "high"
        }
      }
    }
  },
  "msg-sent-timestamp": "2024-10-30 00:09:54"
}
```
- **v2.0 Additions**: Value history, source attribution, priorities.

---

## Installation & Setup

### Prerequisites
- Python 3.8+  
- Node.js 14+  
- npm or yarn

### Quick Start
```bash
# Clone v2.0 Dev Branch
git clone -b Dev2.0V https://github.com/AryanRai/Comms.git
cd Comms

# Install Python dependencies
pip install socketify

# Install UI dependencies
cd ui/ariesUI
npm install
```

### Running the System
- **Via HyperThreader (Recommended)**:
  ```bash
  conda comms
  python HyperThreader.py
  ```
- **Separately**:
  ```bash
  # Start Stream Handler
  cd StreamHandler
  python stream_handlerv2.3.py  # or sh/sh.py for v2.0

  # Start Engine
  cd Engine
  python engine.py  # or en/en.py for v2.0

  # Launch AriesUI
  cd ui/ariesUI
  npm start
  ```

---

## Development Guide

<details>
<summary><b>Creating Custom Modules</b></summary>

### Engine Module Template (v2.0)
```python
class CustomModule:
    def __init__(self):
        self.config = {
            "notify_on_change": True,
            "update_rate": 0.1
        }
        self.streams = {
            "1": Stream(
                stream_id=1,
                name="SensorName",
                datatype="float",
                unit="Units",
                status="active",
                metadata={"sensor": "Model", "precision": 0.1}
            )
        }
        self.debug_messages = []
        self.value_change_history = []

    def _handle_value_change(self, stream_id, old_value, new_value, source="internal"):
        # Track value changes
        pass

    async def update_streams_forever(self):
        # Continuous updates
        pass
```

### UI Widget Development (v2.0)
```jsx
const ControlWidget = ({ streamId }) => {
    const [value, setValue] = useState(0);
    const [status, setStatus] = useState("idle");

    // Control logic here
    return (
        <div className="control-widget">
            {/* Widget content */}
        </div>
    );
};
```

</details>

---

## File Structure
```
Comms/
├── Engine/
│   ├── engine.py           # Main engine process
│   └── DynamicModules/     # Hardware modules
│       ├── hw_module_1.py  # Sample module
│       └── hw_win_serial_chyappy.py  # Serial module
├── StreamHandler/
│   └── stream_handlerv2.3.py  # WebSocket server
├── ui/ariesUI/             # Electron-based UI
│   ├── src/
│   │   ├── App.js         # Main React app
│   │   ├── components/    # React components
│   │   └── assets/        # CSS, JS, etc.
│   └── main.js            # Electron main process
└── HyperThreader.py        # Instance manager
```

---

## Visuals
- **Preloader**: [View](https://github.com/user-attachments/assets/7c4ef414-1c9a-4a61-9ce4-4b4fedfc6127)  
- **AriesUI**: [View](https://github.com/user-attachments/assets/50c152d3-6e9f-4ffd-a809-f051c1da6234)  
- **Toolbox**: [View](https://github.com/user-attachments/assets/0396efcb-73cb-468e-bc73-aa85319d592d)  
- **StreamHandler**: [View](https://github.com/user-attachments/assets/ff4716f3-7659-47ac-afef-24114f4cd9b9)

---

## TODOs
- **Short-Term**: Unique sensor data GUI per grid, fix stream format, add refresh controls.
- **Long-Term**: 3D mode (Three.js), mobile hosting, online Stream Handler with codes.

---

## Contributing
Check out our [Contributing Guidelines](https://www.notion.so/CONTRIBUTING.md). Pull requests are welcome!

## License
[MIT License](LICENSE)

## Contact
📧 [aryanrai170@gmail.com](mailto:aryanrai170@gmail.com)
