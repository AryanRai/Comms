// ui/ariesMods/SliderControl.js
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

log(LogLevels.INFO, 'importing SliderControl');

const SliderControl = ({ streamId }) => {
  const [value, setValue] = React.useState(0);
  const [min, setMin] = React.useState(0);
  const [max, setMax] = React.useState(100);
  const [step, setStep] = React.useState(1);
  const [status, setStatus] = React.useState('');
  const [unit, setUnit] = React.useState('');
  const debounceTimeout = React.useRef(null);

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
      if (data.type === 'config_response' && data.module_id === moduleId) {
        setStatus(`Last update: ${data.status}`);
        log(LogLevels.INFO, 'Config response:', data);
      }
    };

    // Monitor stream value and metadata changes
    const monitorInterval = setInterval(() => {
      const streamData = window.GlobalData?.data?.[moduleId]?.streams?.[streamName];
      if (streamData) {
        setValue(streamData.value);
        setUnit(streamData.unit || '');
        
        // Update range from metadata if available
        if (streamData.metadata) {
          if (streamData.metadata.range) {
            setMin(streamData.metadata.range.min || 0);
            setMax(streamData.metadata.range.max || 100);
          }
          if (streamData.metadata.step) {
            setStep(streamData.metadata.step);
          }
        }
        
        log(LogLevels.DEBUG, `Current value for ${streamId}:`, streamData.value);
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

  const handleSliderChange = (event) => {
    const newValue = parseFloat(event.target.value);
    setValue(newValue);

    // Clear any existing timeout
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    // Set a new timeout to update the value after 100ms of no changes
    debounceTimeout.current = setTimeout(() => {
      if (!streamId) return;

      const [moduleId, streamName] = streamId.split('.');
      
      // Send config update
      if (window.updateModuleConfig) {
        const configUpdate = {
          [`${streamName}_value`]: newValue
        };
        window.updateModuleConfig(moduleId, configUpdate);
        log(LogLevels.INFO, `Sending value update to ${moduleId}:`, newValue);
      } else {
        log(LogLevels.ERROR, 'updateModuleConfig not available');
      }
    }, 100);
  };

  return React.createElement(
    'div',
    { className: 'slider-control p-4 bg-base-200 rounded-lg' },
    React.createElement(
      'div',
      { className: 'flex flex-col gap-4' },
      React.createElement(
        'label',
        { className: 'label' },
        `${streamId || 'No stream selected'} ${unit ? `(${unit})` : ''}`
      ),
      React.createElement(
        'div',
        { className: 'flex items-center gap-4' },
        React.createElement(
          'span',
          { className: 'text-sm' },
          min
        ),
        React.createElement(
          'input',
          {
            type: 'range',
            className: 'range range-primary',
            min: min,
            max: max,
            step: step,
            value: value,
            onChange: handleSliderChange,
            disabled: !streamId
          }
        ),
        React.createElement(
          'span',
          { className: 'text-sm' },
          max
        )
      ),
      React.createElement(
        'div',
        { className: 'text-center' },
        `Value: ${value}`
      ),
      React.createElement(
        'div',
        { className: 'text-sm opacity-70 text-center' },
        status
      )
    )
  );
};

export default SliderControl; 