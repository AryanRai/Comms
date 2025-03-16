# Comms Alpha v2.0 (Dev Branch)

![Comms2.0](https://github.com/user-attachments/assets/02e70432-e6f7-4664-9f17-b6b0acd60a67)

A centralized communications dashboard for multi-layered control in ground stations, all-in-one DAQ solutions, and hardware interfaces. Comms provides a modular, extensible platform for hardware development and monitoring.

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

