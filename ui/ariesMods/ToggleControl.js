const LogLevels = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

const log = (level, message, ...args) => {
  const currentLevel = window.DEBUG_LEVEL || LogLevels.INFO;
  if (level >= currentLevel) {
    const prefix = `[${Object.keys(LogLevels)[level]}]`;
    switch (level) {
      case LogLevels.DEBUG:
        console.debug(prefix, message, ...args);
        break;
      case LogLevels.INFO:
        console.info(prefix, message, ...args);
        break;
      case LogLevels.WARN:
        console.warn(prefix, message, ...args);
        break;
      case LogLevels.ERROR:
        console.error(prefix, message, ...args);
        break;
    }
  }
};

log(LogLevels.INFO, 'importing ToggleControl');

const ToggleControl = ({ streamId }) => {
  const [isToggled, setIsToggled] = React.useState(false);
  const [status, setStatus] = React.useState('');

  React.useEffect(() => {
    if (!streamId) {
      log(LogLevels.WARN, 'Missing streamId');
      return;
    }

    const [moduleId, streamName] = streamId.split('.');
    log(LogLevels.DEBUG, 'Stream:', { moduleId, streamName });

    // Subscribe to control responses
    const handleControlResponse = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'control_response' && data.module_id === moduleId) {
        setStatus(`Last command: ${data.status}`);
        log(LogLevels.INFO, 'Control response:', data);
      }
    };

    // Monitor stream value changes
    const monitorInterval = setInterval(() => {
      const value = window.GlobalData?.data?.[moduleId]?.streams?.[streamName]?.value;
      if (value !== undefined) {
        setIsToggled(value === 1);
        log(LogLevels.DEBUG, `Current value for ${streamId}:`, value);
      }
    }, 100);

    // Add event listener for WebSocket messages
    if (window.ws) {
      window.ws.addEventListener('message', handleControlResponse);
    }

    return () => {
      clearInterval(monitorInterval);
      if (window.ws) {
        window.ws.removeEventListener('message', handleControlResponse);
      }
    };
  }, [streamId]);

  const handleToggle = () => {
    if (!streamId) return;

    const [moduleId, streamName] = streamId.split('.');
    const newValue = !isToggled;
    setIsToggled(newValue);

    // Send control command
    if (window.sendModuleControl) {
      const command = newValue ? 'set_high' : 'set_low';
      window.sendModuleControl(moduleId, command);
      log(LogLevels.INFO, `Sending command: ${command} to ${moduleId}`);
    } else {
      log(LogLevels.ERROR, 'sendModuleControl not available');
    }
  };

  return React.createElement(
    'div',
    { className: 'toggle-control p-4 bg-base-200 rounded-lg' },
    React.createElement(
      'div',
      { className: 'flex flex-col items-center gap-4' },
      React.createElement(
        'label',
        { className: 'label' },
        `Control: ${streamId || 'No stream selected'}`
      ),
      React.createElement(
        'input',
        {
          type: 'checkbox',
          className: 'toggle toggle-primary toggle-lg',
          checked: isToggled,
          onChange: handleToggle,
          disabled: !streamId
        }
      ),
      React.createElement(
        'div',
        { className: 'text-sm opacity-70' },
        status
      )
    )
  );
};

export default ToggleControl; 