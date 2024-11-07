# Comms
Centralized Communications dashboards for multi layered control Ground Stations/all in one DAQ solutions or just tinkering around with hardware.




## Project Overview

### Main Components

This project involves three main components:

Units:

1. Engine + HW Modules (Python)
2. Stream Handler + Stream Transformers (Python + WebSocket)
3. AriesUI + SW Modules (NodeJS + Electron + TailwindCSS + DaisyUI)

Each component is modular and can be built using different frameworks and languages.

----------

### Component Breakdown

#### 1. Engine

-   **Functionality**:  
    The engine manages modules installed for specific hardware types, such as sensors. It can communicate via serial or other methods.
-   **Modules**:  
    Each module creates streams for its hardware variables, updating these values through the engine within the stream handler.
-   **Negotiator**:  
    A class that connects the engine to the stream handler, responsible for publishing data from hardware modules to the stream handler and vice versa.

#### 2. Stream Handler

-   **Role**:  
    A shared space managing stream creation, deletion, and updating. It handles multiple streams across all modules and stores them for later access.
-   **Stream Processor**:  
    It includes conditions, actions, and procedures and transforms streams by applying protocols or message format conversions.

#### 3. Aries UI (User Interface)

-   **Configurable**:  
    Fully configurable UI, allowing users to subscribe to streams to access or modify values based on their setup.
-   **Technologies**:  
    Built with Tailwind CSS and DaisyUI for a streamlined, responsive design.
-   **Example Layouts**:  
    [Gridstack Demo](https://gridstackjs.com/demo/float.html#) provides examples of the UI's dynamic grid capabilities.

----------

### Key Concepts and Terms

#### Actions, Procedures, Conditions, and Readings

-   **Actions**:  
    User-triggered operations.
-   **Procedures**:  
    Collections of actions.
-   **Conditions**:  
    Actions that execute based on real-time readings.

#### Logger

-   **Purpose**:  
    Logs only activated readings and actions to the active module.

#### Streams

-   **Definition**:  
    Each data exchange is referred to as a stream, encompassing both actions and readings.
-   **Syncing**:  
    A list of streams syncs between the front end and back end and can be configured to be one-sided if needed.

#### Profiles _(to be renamed)_

-   **Purpose**:  
    Store the dashboard layout, streams, and associated hardware configurations.
-   **Local Storage**:  
    Profiles can be saved locally and can contain multiple dashboard layouts.

----------

### Modules and Extensions

#### Types of Modules

-   **JavaScript Extensions**:  
    Enhance functionality.
-   **UI Extensions**:  
    Add or beautify the UI.
-   **Backend Hardware Extensions**:  
    Allow new hardware interfaces or combinations of features.

#### Module Types

1.  **Engine Modules**
2.  **Stream Handler Modules**
    -   **Conditions, Actions, Procedures**
    -   **Stream Processor**
3.  **UI Modules**:  
    **Aries UI and Aries Modules**

Each software module can operate independently across different devices.

#### Comms/Hardware Modules

-   **Hardware Wrappers**:  
    Modules act as wrappers for physical hardware, interfacing with the engine and informing the system about available streams and actions.
-   **Customizable UI**:  
    UI can be customized based on the active modules.

----------

### AriesUI & AriesMods

-   **AriesUI**:  
    Built with Tailwind and DaisyUI for streamlined, adaptable design.
-   **AriesMods**:  
    Includes pages, elements, and profile examples.


----------


## Current Sample 
The current sample tests end to end conectivity of from data being sent over the DynamicModules -> Engine -> Stream Handler (Websockets) -> AriesUI

##Testing Modules
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

