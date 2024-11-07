
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
git clone https://github.com/AryanRai/Comms.git
cd Comms
```

Install Python dependencies:
```bash
pip install socketify
```

Install UI dependencies:
```bash
cd Gui/ariesUI
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
   cd Gui/ariesUI
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
Received message: {"type": "negotiation", "status": "active", "data": {"hw_module_1": {"module_id": "hw_module_1", "name": "Hw Module 1", "status": "active", "module-update-timestamp": "2024-10-30 00:09:32", "config": {"update_rate": 1.0, "temperature_range": {"min": -50, "max": 150}, "pressure_range": {"min": 800, "max": 1200}, "enabled_streams": ["stream1", "stream2"], "debug_mode": false}, "streams": {"stream1": {"stream_id": 1, "name": "Temperature", "datatype": "float", "unit": "Celsius", "status": "active", "metadata": {"sensor": "TMP36", "precision": 0.1, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 120.2127922110659, "stream-update-timestamp": "2024-10-30 00:09:53", "priority": "high"}, "stream2": {"stream_id": 2, "name": "Pressure", "datatype": "float", "unit": "hPa", "status": "active", "metadata": {"sensor": "BMP180", "precision": 0.5, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 888.8849471853615, "stream-update-timestamp": "2024-10-30 00:09:53", "priority": "high"}}}, "hw_win_serial_chyappy": {"module_id": "hw_win_serial_chyappy", "name": "Hw Win Serial Chyappy", "status": "active", "module-update-timestamp": "2024-10-30 00:09:32", "config": {}, "streams": {"1": {"stream_id": 1, "name": "Temperature", "datatype": "float", "unit": "Celsius", "status": "active", "metadata": {"sensor": "TMP36", "precision": 0.1, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 0, "stream-update-timestamp": "2024-10-30 00:09:32", "priority": "high"}, "2": {"stream_id": 2, "name": "Pressure", "datatype": "float", "unit": "hPa", "status": "active", "metadata": {"sensor": "BMP180", "precision": 0.5, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 0, "stream-update-timestamp": "2024-10-30 00:09:32", "priority": "high"}}}}, "msg-sent-timestamp": "2024-10-30 00:09:54"}

### Stream Selection Gui
![image](https://github.com/user-attachments/assets/ba7ecb42-1fba-4d65-bc28-8477beaca852)

### UI Recieving Data from Stream Handler
![image](https://github.com/user-attachments/assets/9c8642e5-6c17-42df-8faa-8fa481cfd1d8)

### Dragable Grids and Nested Grids
![image](https://github.com/user-attachments/assets/148d09b0-a52f-4c8b-aee9-f1c34ee4e222)

![image](https://github.com/user-attachments/assets/f79ef7a3-3876-4168-949f-1ed639d7f01a)


# TODO 
TODO need to implement GUI displaying customizable unique sensor data within each grid 

Working sample on top of page

![image](https://github.com/user-attachments/assets/4869b3b4-6613-471d-94e8-281d80b6f76d)


# Side Quests:
This was the first prototype that inspired it all. Labjack is a very precise data acquisition hardware. I wanted to test out a valve and read & log data from a pressure transducer at around 1000Hz. Labjack has their own libraries for reading data from analogue pins of a labjack hence this was born.

Labjack Valve testing UI: 

![Demo](https://github.com/user-attachments/assets/8e359429-59c5-40ae-935f-43ecbb8c98da)



#Ideas

conditions, actions, and procedures 

