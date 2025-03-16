# Comms Alpha v2.0 (Dev Branch)

![Comms2.0](https://github.com/user-attachments/assets/02e70432-e6f7-4664-9f17-b6b0acd60a67)

A centralized communications dashboard for multi-layered control in ground stations, all-in-one DAQ solutions, and hardware interfaces. Comms provides a modular, extensible platform for hardware development and monitoring.

## Project Overview

### Versions

- **Alpha v1.0**: First stable release (unreleased, scheduled). Focuses on one-way communication and core functionality.
- **Alpha v2.0 (Dev Branch)**: Adds two-way communication, enhanced stream management, new control widgets, and performance improvements.

### Core Components

1. **Engine + Dynamic Modules (Python)**
Manages hardware interfaces and data streams.
2. **Stream Handler + Stream Transformers (Python + WebSocket)**
Handles real-time data flow between Engine and UI.
3. **AriesUI + Aries Modules (NodeJS + Electron + TailwindCSS + DaisyUI)**
Provides a customizable, grid-based dashboard UI.
- **Modularity**: Each component can run independently on different devices and be built with various frameworks/languages.
- **HyperThreader**: Manages, runs, and debugs all instances concurrently.

---

## System Architecture

### Engine (aka "en")

- **Role**: Core processing layer for hardware communications.
- **Features**:
    - Dynamic module loading with safe initialization.
    - Async operation support.
    - Hardware interface abstraction.
    - Configurable update rates (default 100ms in v2.0).
    - Error handling, recovery, and debug message propagation.
    - Value change notification system (v2.0).
- **DynamicModules (DynMods)**:
    - Wrappers for hardware (e.g., sensors) with communication methods (serial, etc.).
    - Creates streams for hardware variables, updating them via the Engine.
    - Examples: Serial Communication, Random Number Generator (test), Custom Hardware Templates.
    - **Negotiator Class**: Links Engine to Stream Handler, publishing/receiving data.

### Stream Handler (aka "sh")

- **Role**: Manages data flow between Engine and UI.
- **Features**:
    - WebSocket-based communication (Socketify, 100ms idle timeout in v2.0).
    - Message queuing, priority-based routing, and compression.
    - Real-time stream creation, deletion, and updates.
    - Debug interface with pause/resume (v2.0).
    - Configurable refresh rates (v2.0).
- **Streams**:
    - Data exchanges (actions, readings) synced between frontend and backend.
    - Configurable as one-sided or bidirectional (v2.0).
- **Logger**: Logs activated readings and actions.
- **Stream Transformer/Interpreter**: Applies protocol/message format conversions.

### AriesUI (aka "ui")

- **Role**: User interface for visualization and control.
- **Features**:
    - Customizable grid layout (Gridstack) with drag-and-drop widgets.
    - Real-time data visualization and monitoring.
    - Module configuration and status monitoring.
    - New control widgets (v2.0): Toggle, Slider, Value Monitor.
    - Responsive to rate changes and enhanced error feedback (v2.0).
- **AriesMods**:
    - Extensions: JavaScript (functionality), UI (design/function), Backend Hardware (interfaces), or combinations.
    - **Marketplace**: Centralized page for adding modules.
- **Profiles (Suggest a New Name)**:
    - Stores dashboard layouts, streams, and hardware configs.
    - Saved locally, supports multiple layouts.

---

## Core Features

### Alpha v1.0 (Currently Implemented)

- One-way end-to-end communication, data acquisition, and visualization.
- Engine with custom plugins and DynamicModules.
- Stream Handler with WebSocket streaming.
- AriesUI with dynamic, customizable dashboards.
- AriesMods: Drag-and-drop widgets, live data visualization, community marketplace.
- HyperThreader for managing instances.

### Alpha v2.0 (New Features)

- **Two-Way Communication**: Bidirectional control with real-time feedback.
- **Enhanced Stream Management**: Metadata handling, value change tracking, stream priorities.
- **New Control Widgets**: Toggle (binary), Slider (continuous), Value Monitor (history tracking).
- **Performance Improvements**: 100ms default update rate, configurable via HyperThreader, optimized WebSocket usage.
- **Debug Features**: Comprehensive logging, command history, real-time status updates.

---

## What's New in v2.0

### Two-Way Communication
- Full bidirectional communication between UI and hardware modules
- Real-time control capabilities with instant feedback
- Enhanced error handling and status reporting
- Configurable update rates for each component through HyperThreader

### Enhanced Stream Management
- Automatic stream metadata handling
- Value change notifications and history tracking
- Configurable stream priorities
- Improved error detection and recovery
- Centralized update rate configuration

### New Control Widgets
1. **Toggle Control**
   - Binary state control (0/1)
   - Real-time status feedback
   - Visual state indication
   - Error state handling

2. **Slider Control**
   - Continuous value control
   - Auto-range detection from stream metadata
   - Real-time value display
   - Unit display support
   - Debounced updates
   - Min/max range validation

3. **Value Monitor**
   - Change history tracking
   - Timestamp-based monitoring
   - Source attribution (UI vs. Internal)
   - Configurable notification thresholds

### Performance Improvements
- Default 100ms update rate across all components
- Configurable update rates through HyperThreader:
  - Performance monitor refresh rate
  - Terminal output refresh rate
  - Engine update rate
  - Negotiator rate
  - Individual module update rates
- Reduced network overhead with optimized WebSocket settings
- Better memory management
- Enhanced error recovery
- Real-time rate adjustments without restart

### Debug Features
- Comprehensive logging system
- Value change tracking
- Command history
- Real-time status updates
- Debug windows for each component:
  - Stream Handler Debug: Configurable refresh rate and pause functionality
  - Engine Debug: Configurable refresh rate and module expansion
  - Configuration windows for all components

## Core Components

### Engine (v2.0)
- Dynamic module loading with safe initialization
- Configurable update rates per module
- Enhanced error handling and recovery
- Debug message propagation
- Value change notification system
- Real-time configuration updates

### Stream Handler (v2.0)
- Improved WebSocket management with 100ms idle timeout
- Configurable refresh rates
- Enhanced message compression
- Priority-based message routing
- Debug interface with pause/resume
- Real-time configuration updates

### HyperThreader (v2.0)
- Centralized control interface
- Universal update rate configuration
- Real-time performance monitoring
- Component-specific configuration windows
- Improved terminal output control
- System-wide debug level management

### AriesUI (v2.0)
- New control widgets
- Enhanced grid layout system
- Real-time value monitoring
- Improved error feedback
- Status indicators for all components
- Responsive to rate changes


## Stream Format

### Standard Message Format (v1.0 & v2.0)

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

- **v2.0 Additions**: Value change history, source attribution (UI vs. internal), configurable priorities.

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Quick Start

```bash
# Clone repository (v2.0 Dev Branch)
git clone -b Dev2.0V <https://github.com/AryanRai/Comms.git>
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

### Creating Custom Modules

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

---

## File Structure

```
Comms/
├── Engine/
│   ├── engine.py           # Main engine process
│   └── DynamicModules/     # Hardware interface modules
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

- **Preloader**: [Image](https://github.com/user-attachments/assets/7c4ef414-1c9a-4a61-9ce4-4b4fedfc6127)
- **AriesUI**: [Image](https://github.com/user-attachments/assets/50c152d3-6e9f-4ffd-a809-f051c1da6234)
- **Toolbox**: [Image](https://github.com/user-attachments/assets/0396efcb-73cb-468e-bc73-aa85319d592d)
- **StreamHandler**: [Image](https://github.com/user-attachments/assets/ff4716f3-7659-47ac-afef-24114f4cd9b9)

---

## TODOs

- **Short-Term**: GUI for unique sensor data per grid, fix stream format inconsistencies, add refresh rate controls.
- **Long-Term**: 3D mode with Three.js, local hosting for mobile access, online Stream Handler with unique codes.

---

## Contributing

See [Contributing Guidelines](https://www.notion.so/CONTRIBUTING.md). Pull requests welcome!

## License

[MIT License]

## Contact

[aryanrai170@gmail.com]
