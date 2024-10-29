# Comms
Centralized Communications dashboards for multi layered control Ground Stations/all in one DAQ solutions or just tinkering around with hardware.

Units:

1. Engine + HW Modules (Python)
2. Stream Handler + Stream Transformers (Python + WebSocket)
3. AriesUI + SW Modules (NodeJS + Electron + TailwindCSS + DaisyUI)


Current Sample DynamicModules
RandomNumberGenerator (Testing Template)
SerialReaderChyappy (read from Lora using esp32 send over serial)

#Images
Preloader
![image](https://github.com/user-attachments/assets/7c4ef414-1c9a-4a61-9ce4-4b4fedfc6127)

AriesUI
![image](https://github.com/user-attachments/assets/50c152d3-6e9f-4ffd-a809-f051c1da6234)

Toolbox
![image](https://github.com/user-attachments/assets/0396efcb-73cb-468e-bc73-aa85319d592d)

StreamHandler
![image](https://github.com/user-attachments/assets/ff4716f3-7659-47ac-afef-24114f4cd9b9)

Sample Msg 
Received message: {"type": "negotiation", "status": "active", "data": {"hw_module_1": {"module_id": "hw_module_1", "name": "Hw Module 1", "status": "active", "module-update-timestamp": "2024-10-30 00:09:32", "config": {"update_rate": 1.0, "temperature_range": {"min": -50, "max": 150}, "pressure_range": {"min": 800, "max": 1200}, "enabled_streams": ["stream1", "stream2"], "debug_mode": false}, "streams": {"stream1": {"stream_id": 1, "name": "Temperature", "datatype": "float", "unit": "Celsius", "status": "active", "metadata": {"sensor": "TMP36", "precision": 0.1, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 120.2127922110659, "stream-update-timestamp": "2024-10-30 00:09:53", "priority": "high"}, "stream2": {"stream_id": 2, "name": "Pressure", "datatype": "float", "unit": "hPa", "status": "active", "metadata": {"sensor": "BMP180", "precision": 0.5, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 888.8849471853615, "stream-update-timestamp": "2024-10-30 00:09:53", "priority": "high"}}}, "hw_win_serial_chyappy": {"module_id": "hw_win_serial_chyappy", "name": "Hw Win Serial Chyappy", "status": "active", "module-update-timestamp": "2024-10-30 00:09:32", "config": {}, "streams": {"1": {"stream_id": 1, "name": "Temperature", "datatype": "float", "unit": "Celsius", "status": "active", "metadata": {"sensor": "TMP36", "precision": 0.1, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 0, "stream-update-timestamp": "2024-10-30 00:09:32", "priority": "high"}, "2": {"stream_id": 2, "name": "Pressure", "datatype": "float", "unit": "hPa", "status": "active", "metadata": {"sensor": "BMP180", "precision": 0.5, "location": "main_chamber", "calibration_date": "2024-10-30"}, "value": 0, "stream-update-timestamp": "2024-10-30 00:09:32", "priority": "high"}}}}, "msg-sent-timestamp": "2024-10-30 00:09:54"}

Stream Selection Gui
![image](https://github.com/user-attachments/assets/ba7ecb42-1fba-4d65-bc28-8477beaca852)

UI Recieving Data from Stream Handler
![image](https://github.com/user-attachments/assets/9c8642e5-6c17-42df-8faa-8fa481cfd1d8)

Dragable Grids and Nested Grids
![image](https://github.com/user-attachments/assets/148d09b0-a52f-4c8b-aee9-f1c34ee4e222)

![image](https://github.com/user-attachments/assets/f79ef7a3-3876-4168-949f-1ed639d7f01a)

TODO need to implement GUI displaying customizable unique sensor data within each grid 

Working sample on top of page

![image](https://github.com/user-attachments/assets/4869b3b4-6613-471d-94e8-281d80b6f76d)


Side Quests:
Labjack Valve testing UI: 

![Demo](https://github.com/user-attachments/assets/8e359429-59c5-40ae-935f-43ecbb8c98da)

