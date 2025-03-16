# Comms Alpha v2.0 (Dev Branch)

![Comms2.0](https://github.com/user-attachments/assets/02e70432-e6f7-4664-9f17-b6b0acd60a67)

![Demo D 2.0](https://github.com/user-attachments/assets/18b8ee39-91ae-4da7-9e41-55d9d223c02a)

# Comms Alpha v1.0 
#First Official Stable Release Scheduled

A centralized communications dashboard for multi-layered control in ground stations, all-in-one DAQ solutions, and hardware interfaces. Comms provides a modular, extensible platform for hardware development and monitoring.

![Comms1.0](https://github.com/user-attachments/assets/7de95c4d-412d-469c-b0d5-79d940087ebe)

![Demo D 1.0](https://github.com/user-attachments/assets/1940eeb6-21f9-4bb1-915e-4e18014a87e3)


[Notion Tracker](https://green-croissant-260.notion.site/2bd3cc2581c94ca6b16c0f801b337208?v=1adeb3eb3974800d985f000ca6a61924)


## Latest Updates

### Configurable Update Rates
- All system components now support configurable update rates:
  - Performance monitor refresh rate
  - Terminal output refresh rate
  - Engine update rate
  - Negotiator update rate
  - Individual module update rates
- Default 100ms refresh rate for responsive real-time updates
- Configurable through HyperThreader's "Configure Update Rates" interface

### Enhanced Debug Features
- Debug level control (0-2) for all components
- Real-time performance metrics with visual indicators
- Improved error handling and status reporting
- Module-specific configuration options

### Improved UI Features
- Visual performance metrics with CPU and memory usage bars
- Organized button layout with clear section grouping
- Enhanced terminal output control
- Real-time module status updates

## Core Components

### HyperThreader
- Centralized control interface for all system components
- Real-time performance monitoring with visual metrics
- Configurable update rates for all components
- Organized section-based controls for SH, EN, and UI
- Enhanced terminal output management

### Engine Layer
- Dynamic module loading with configurable update rates
- Real-time module status monitoring
- Enhanced error handling and recovery
- Debug level control for verbose output
- Module-specific configuration management

### Stream Handler Layer
- WebSocket-based communication with configurable idle timeout
- Message queuing with priority support
- Real-time connection management
- Configurable refresh rates for debug window
- Enhanced error handling and status reporting

### AriesUI Layer
- Real-time data visualization with configurable refresh rates
- Customizable grid layout system
- Module configuration interface
- Status monitoring with visual indicators
- Enhanced logging controls

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Setup Steps
```bash
# Clone repository
git clone -b Dev2.0V https://github.com/AryanRai/Comms.git
cd Comms

# Install Python dependencies
pip install socketify

# Install UI dependencies
cd ui/ariesUI
npm install
```

### Running the System

#### Using HyperThreader (Recommended)
```bash
# Start HyperThreader
python HyperThreader.py
```

#### Running Components Separately
```bash
# Start Stream Handler
cd sh
python sh.py

# Start Engine
cd en
python en.py

# Launch AriesUI
cd ui/ariesUI
npm start
```

## Configuration

### Update Rates
Access the configuration window through HyperThreader:
1. Click "Configure Update Rates"
2. Adjust rates for:
   - Performance Monitor
   - Terminal Output
   - Engine
   - Negotiator
   - Individual Modules
3. Set Debug Level (0-2)
4. Apply changes

### Module Configuration
Each module supports:
- Custom update rate
- Debug mode toggle
- Module-specific settings
- Stream configuration

## Development Guide

### Creating Custom Modules

#### Module Template
```python
class CustomModule:
    def __init__(self):
        self.config = {
            'update_rate': 0.1,  # 100ms default
            'debug_mode': False,
            'enabled_streams': ['stream1']
        }
        self.streams = self._initialize_streams()

    async def update_streams_forever(self):
        while True:
            # Update logic here
            await asyncio.sleep(self.config['update_rate'])
```

### UI Widget Development
```html
<div class="grid-stack-item" gs-w="2" gs-h="1">
    <div class="grid-stack-item-content">
        <!-- Widget content -->
    </div>
</div>
```

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
[Add License Information]

## Contact
[Add Contact Information]

---

# Comms

A centralized communications dashboard for multi-layered control in ground stations, all-in-one DAQ solutions, or tinkering with hardware.

This project was motivated by working on various hardware and embedded systems with multiple sensors, motors, and actuators, each connected to different processors (e.g., Arduinos, STM32s, Labjacks). These processors often communicate with ground stations, data acquisition, or logging systems over different media. The goal here is to allow more focus on hardware development without worrying about software.

---

## Project Overview

### Main Components

This project includes three main components:

1. **Engine + Dynamic Modules (Python)**
2. **Stream Handler + Stream Transformers (Python + WebSocket)**
3. **AriesUI + SW Modules (NodeJS + Electron + TailwindCSS + DaisyUI)**

Each component is modular and can be built using various frameworks and languages.

---

### Component Breakdown

#### 1. Engine
- **Functionality**: Manages hardware-specific modules, such as sensors, which communicate via serial or other methods.
- **DynamicModules**: Custom code modules for hardware communication. See [Serial Chyappy Module](https://github.com/AryanRai/Comms/blob/main/Engine/DynamicModules/hw_win_serial_chyappy.py) as an example.
- **Streams**: Each module creates streams for its hardware variables, updating these values through the engine within the stream handler.

Example data structure:
~~~python
streams = {
    '1': Stream(
        stream_id=1,
        name="Temperature",
        datatype="float",
        unit="Celsius",
        status="active",
        metadata={"sensor": "TMP36", "precision": 0.1, "location": "main_chamber", "calibration_date": datetime.now().strftime("%Y-%m-%d")}
    ),
    '2': Stream(
        stream_id=2,
        name="Pressure",
        datatype="float",
        unit="hPa",
        status="active",
        metadata={"sensor": "BMP180", "precision": 0.5, "location": "main_chamber", "calibration_date": datetime.now().strftime("%Y-%m-%d")}
    )
}
~~~
Each module has a `run()` function to execute the module in an async loop.

#### 2. Stream Handler
- **Role**: Acts as a shared space managing stream creation, deletion, and updating. Built in Python using Socketify for WebSocket management, it receives messages from the engine and broadcasts them to AriesUI.

#### 3. Aries UI (User Interface)
- **Configurable**: Fully configurable dashboard grid UI, where users subscribe to streams for real-time data access or modification.
- **Technologies**: Built with React, Tailwind CSS, and DaisyUI.
- **Example Layouts**: [Gridstack Demo](https://gridstackjs.com/demo/float.html#) demonstrates dynamic grid capabilities.

---

# Comms Documentation

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation Steps

Clone the repository:
```bash
git clone -b Dev2.0V https://github.com/AryanRai/Comms.git
cd Comms
```

Install Python dependencies:
```bash
pip install socketify
```

Install UI dependencies:
```bash
cd ui/ariesUI
npm install
```

### Running the System

1. Start the Stream Handler:
   ```bash
   cd StreamHandler
   python stream_handlerv2.3.py
   ```

2. Start the Engine:
   ```bash
   cd Engine
   python engine.py
   ```

3. Launch AriesUI:
   ```bash
   cd ui/ariesUI
   npm start
   ```

---

## Component Details

### Stream Handler (stream_handlerv2.3.py)
The Stream Handler manages WebSocket connections, broadcasts messages, and compresses data. 

### Stream Interface (stream_interface.js)
Manages WebSocket connections from the UI side and supports active stream querying, status updates, and connection management.

### AriesUI Dashboard (dashv1.9.html)
Provides a flexible grid-based interface:
- Draggable/resizable widgets
- Nested grid support
- Real-time data visualization
- Status bar with system information

---

## Creating Custom Modules

### Dynamic Module Template

Example structure:
~~~python
class MyCustomModule:
    def __init__(self):
        self.streams = {
            '1': Stream(
                stream_id=1,
                name="SensorName",
                datatype="float",
                unit="Units",
                status="active",
                metadata={"sensor": "SensorModel", "precision": 0.1, "location": "sensor_location", "calibration_date": datetime.now().strftime("%Y-%m-%d")}
            )
        }

    async def run(self):
        # Implementation for data collection/processing
        pass
~~~

---

### UI Widget Development
Add widgets using the grid system:
~~~html
<div class="grid-stack-item" gs-w="2" gs-h="1">
    <div class="grid-stack-item-content">
        <!-- Widget content -->
        <button class="chunky-btn" onClick="grid.removeWidget(this.parentNode.parentNode)">X</button>
        <button class="chunky-btn" onclick="my_modal_2.showModal()">Configurator</button>
        <!-- Custom widget content here -->
    </div>
</div>
~~~

## Current Sample
Testing end-to-end connectivity from DynamicModules → Engine → Stream Handler (Websockets) → AriesUI.

### Sample Message
Example message received by Aries UI from a sensor:
```json
{
  "type": "negotiation",
  "status": "active",
  "data": {
    "hw_module_1": {
      "module_id": "hw_module_1",
      "name": "Hw Module 1",
      "status": "active",
      ...
    }
  },
  "msg-sent-timestamp": "2024-10-30 00:09:54"
}
```

---

### TODO 
Implement GUI for displaying customizable unique sensor data within each grid


## Current Sample 
The current sample tests end to end conectivity of from data being sent over the DynamicModules -> Engine -> Stream Handler (Websockets) -> AriesUI

## Testing Modules
-RandomNumberGenerator (Testing Template)
-SerialReaderChyappy (read from Lora using esp32 send over serial)

Images

## Preloader
![image](https://github.com/user-attachments/assets/7c4ef414-1c9a-4a61-9ce4-4b4fedfc6127)

## AriesUI
![image](https://github.com/user-attachments/assets/50c152d3-6e9f-4ffd-a809-f051c1da6234)

## Toolbox
![image](https://github.com/user-attachments/assets/0396efcb-73cb-468e-bc73-aa85319d592d)

## StreamHandler
![image](https://github.com/user-attachments/assets/ff4716f3-7659-47ac-afef-24114f4cd9b9)

### Sample Msg
A sample message recieved by the Aries UI from a sensor 

```
Received message: {"type": "negotiation", "status": "active", "data": {"hw_module_1": {"module_id": "hw_module_1", "name": "Hw Module 1", "status": "active", "module-update-timestamp": "2024-10-30 00:09:32", "config": {"update_rate": 1.0, "temperature_range": {"min": -50, "max": 150}, "pressure_range": {"min": 800, "max": 1200}, "enabled_streams": ["stream1", "stream2"], "debug_mode": false}, "streams": {"stream1": {"stream_id": 1, "name": "Temperature", "datatype": "float", "unit": "Celsius", "status": "active", "metadata": {"sensor": "TMP36", "precision": 0.1, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 120.2127922110659, "stream-update-timestamp": "2024-10-30 00:09:53", "priority": "high"}, "stream2": {"stream_id": 2, "name": "Pressure", "datatype": "float", "unit": "hPa", "status": "active", "metadata": {"sensor": "BMP180", "precision": 0.5, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 888.8849471853615, "stream-update-timestamp": "2024-10-30 00:09:53", "priority": "high"}}}}, "hw_win_serial_chyappy": {"module_id": "hw_win_serial_chyappy", "name": "Hw Win Serial Chyappy", "status": "active", "module-update-timestamp": "2024-10-30 00:09:32", "config": {}, "streams": {"1": {"stream_id": 1, "name": "Temperature", "datatype": "float", "unit": "Celsius", "status": "active", "metadata": {"sensor": "TMP36", "precision": 0.1, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 0, "stream-update-timestamp": "2024-10-30 00:09:32", "priority": "high"}, "2": {"stream_id": 2, "name": "Pressure", "datatype": "float", "unit": "hPa", "status": "active", "metadata": {"sensor": "BMP180", "precision": 0.5, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 0, "stream-update-timestamp": "2024-10-30 00:09:32", "priority": "high"}}}}, "msg-sent-timestamp": "2024-10-30 00:09:54"}
```

### Stream Selection Gui
![image](https://github.com/user-attachments/assets/ba7ecb42-1fba-4d65-bc28-8477beaca852)

### UI Recieving Data from Stream Handler
![image](https://github.com/user-attachments/assets/9c8642e5-6c17-42df-8faa-8fa481cfd1d8)

### Dragable Grids and Nested Grids
![image](https://github.com/user-attachments/assets/148d09b0-a52f-4c8b-aee9-f1c34ee4e222)

![image](https://github.com/user-attachments/assets/f79ef7a3-3876-4168-949f-1ed639d7f01a)

Working sample on top of page; this is currently just a single senor value being displayed. data is being read from and esp32 over serial chyappy and the esp32 itself is recieving data over lora from another esp32 transmitting over lora

![image](https://github.com/user-attachments/assets/4869b3b4-6613-471d-94e8-281d80b6f76d)

# TODO 
TODO need to implement GUI displaying customizable unique sensor data within each grid 


# TODO

- [x]  Dashboard position
- [x]  Toggles to stop overflow
- [x]  Disable Navbar
- [x]  Message Queue as a log terminal in GUI with time
- [x]  timestamp-based CSV naming
- [x]  Download css local
- [x]  log live
- [x]  disable differential pair
- [ ]  

- [x]  fix stream_handler disconnect problem
- [ ]  Add Priority Strem handler
- [ ]  MultiPub Stream Handler
- [x]  websocket Reconnect AriesUI
- [x]  Look into other websocket librarys
- [ ]  Implement Port, Uri, refresh speed, selection on UI with soft limiter on speed
- [x]  implement status bar
- [x]  use async and combine with current engine implementation
- [ ]  add refresh rate to the msg format for both gui and engine to understand and use automatically dynamicrefresh
- [ ]  implement controling each unit SH, ITF, Engine from AriesUI Live dropdown
- [ ]  Seperate SH and ITF and implement run and kill for each module
- [ ]  add one way or two way and write permissions to stream format
- [ ]  check server live status every couple seconds when link bar open
- [ ]  add heatbeat that send periodic refreshsignals for data such as activestream querys and online status and sync this with top moving bar
- [ ]  add grid box ids and a dict of box ids to corresponding stream ids
- [ ]  copy sensor data ui from v0
- [x]  copy esploraserial module from chatgpt
- [x]  fix dynamic import
- [ ]  fix hw_module_update_forever random values enable thing within hw_module_1
- [ ]  fix stream format where stream id is referenced twice
- [ ]  fix the structure of hw_win_serial_chyappy to have a config dict and more similar to hw_module_1
- [ ]  migrate to node gridstack module from cdn
- [ ]  fix grid iding system for drag drop specially for configurBLE BOXES

# Long Term Todo

- [ ]  Add a 3d mode where 3js render 3d models with sensor readings
- [ ]  a local hosting capabilities so that the webpage can be accessed via a mobile
- [ ]  host stream handler online such that the web page can be accessed from anywhere via unique codes


# Side Quests:
This was the first prototype that inspired it all. Labjack is a very precise data acquisition hardware. I wanted to test out a valve and read & log data from a pressure transducer at around 1000Hz. Labjack has their own libraries for reading data from analogue pins of a labjack hence this was born.

Labjack Valve testing UI: 

![Demo](https://github.com/user-attachments/assets/8e359429-59c5-40ae-935f-43ecbb8c98da)

---

# File Struc


Comms/

├── Engine/

│ ├── engine.py # Main engine process

│ └── DynamicModules/ # Hardware interface modules

│ ├──  init.py

│ ├── hw_module_1.py # Sample module template

│ └── hw_win_serial_chyappy.py # Serial communication module

│

├── StreamHandler/

│ └── stream_handlerv2.3.py # WebSocket server for data streaming

│

└── Gui/

└── ariesUI/ # Electron-based UI

├── src/

│ ├── App.js # Main React application

│ ├── index.js # Entry point

│ ├── components/ # React components

│ │ ├── GridContainer.jsx

│ │ └── SensorDisplay.jsx

│ ├── assets/

│ │ ├── css/

│ │ │ ├── aresv2.css

│ │ │ └── gridstackdemo.css

│ │ └── js/

│ │ ├── core/

│ │ │ └── bundle.js

│ │ └── logic/

│ │ └── stream_interface.js

│ ├── archive/

│ │ └── dashv1.9.html # Previous dashboard version

│ └── preloader.html # Loading screen

├── main.js # Electron main process

├── .babelrc # Babel configuration

├── webpack.config.js # Webpack configuration

├── package.json # Node dependencies

└── package-lock.json

### Key Components

1. **Engine/**

- Core engine process managing hardware modules

- DynamicModules for hardware interfaces

- Extensible module system for different hardware types

2. **StreamHandler/**

- WebSocket server handling data streams

- Manages communication between Engine and UI

- Broadcasts updates to connected clients

3. **Gui/ariesUI/**

- Electron-based desktop application

- React components for UI elements

- Grid-based dashboard system

- Asset management (CSS, JS, images)

- Build configuration files

### Configuration Files

- `.babelrc`: JavaScript transpilation settings

- `webpack.config.js`: Module bundling configuration

- `package.json`: Node.js dependencies and scripts

### Development Files

- Source code in `src/`

- Component definitions in `components/`

- Styling in `assets/css/`

- Logic handlers in `assets/js/`

- Archive of previous versions

This structure shows how the project is organized into distinct components while maintaining modularity and separation of concerns.

# Potential Ideas

---

### Key Concepts and Terms

- **Actions**: User-triggered operations.
- **Procedures**: Collections of actions.
- **Conditions**: Actions based on real-time readings.

#### Logger
Logs activated readings and actions to the active module.

#### Streams
Each data exchange is a stream, encompassing both actions and readings. They sync between the front and back ends.

#### Profiles _(to be renamed)_
Profiles store dashboard layouts, streams, and hardware configurations. They can be saved locally and contain multiple dashboard layouts.

#### Modules and Extensions
Modules are categorized into:
1. Engine Modules
2. Stream Handler Modules (Conditions, Actions, Procedures)
3. UI Modules (Aries UI and Aries Modules)

---

### AriesUI & AriesMods
- **AriesUI**: Built with Tailwind and DaisyUI.
- **AriesMods**: Adds elements and profile examples.

---

conditions, actions, and procedures 

## What's New in v2.0

### Two-Way Communication
- Full bidirectional communication between UI and hardware modules
- Real-time control capabilities with instant feedback
- Enhanced error handling and status reporting
- Configurable update rates for each component

### Enhanced Stream Management
- Automatic stream metadata handling
- Value change notifications and history tracking
- Configurable stream priorities
- Improved error detection and recovery

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
- Optimized update rates (100ms default)
- Reduced network overhead
- Better memory management
- Enhanced error recovery

### Debug Features
- Comprehensive logging system
- Value change tracking
- Command history
- Real-time status updates
- Debug windows for each component

## Core Components

### Engine (v2.0)
- Dynamic module loading with safe initialization
- Configurable update rates per module
- Enhanced error handling and recovery
- Debug message propagation
- Value change notification system

### Stream Handler (v2.0)
- Improved WebSocket management
- Configurable idle timeout
- Enhanced message compression
- Priority-based message routing
- Debug interface with pause/resume

### AriesUI (v2.0)
- New control widgets
- Enhanced grid layout system
- Real-time value monitoring
- Improved error feedback
- Status indicators for all components

---

# Previous Release: Comms Alpha v1.0

[Previous version content remains unchanged...]

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Quick Start
```bash
# Clone repository
git clone -b Dev2.0V https://github.com/AryanRai/Comms.git
cd Comms

# Install Python dependencies
pip install socketify

# Install UI dependencies
cd ui/ariesUI
npm install
```

### Running the System
```bash
# Start HyperThreader (Recommended)
conda comms
python HyperThreader.py

# Or run components separately:
# Start Stream Handler
python sh/sh.py

# Start Engine
python en/en.py

# Launch AriesUI
cd ui/ariesUI
npm start
```

## Development Guide

### Creating Custom Modules

#### Module Template with Value Change Notifications
```python
class CustomModule:
    def __init__(self):
        self.config = {
            'notify_on_change': True,
            'update_rate': 0.1
        }
        self.streams = self._initialize_streams()
        self.debug_messages = []
        self.value_change_history = []

    def _handle_value_change(self, stream_id, old_value, new_value, source="internal"):
        # Implementation for tracking value changes
        pass

    async def update_streams_forever(self):
        # Implementation for continuous updates
        pass
```

### UI Widget Development
```javascript
const ControlWidget = ({ streamId }) => {
    const [value, setValue] = useState(0);
    const [status, setStatus] = useState('idle');

    // Implementation for control logic
    return (
        <div className="control-widget">
            {/* Widget content */}
        </div>
    );
};
```

## Contributing
Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## License
[Add License Information]

## Contact
[Add Contact Information]

