// Global variables
let count = 0;
let gridItemCounter = 0;
// Add a list to store all widget IDs
let widgetIds = [];

const availableWidgets = []; // Array to hold the available widgets

// Add function to generate unique IDs
function generateUniqueId(prefix = 'widget') {
  const uniqueId = `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  widgetIds.push(uniqueId);
  
  return uniqueId;
}

// Sub-grid data
const sub1 = [
  { x: 0, y: 0 },
  { x: 1, y: 0 },
  { x: 2, y: 0 },
  { x: 3, y: 0 },
  { x: 0, y: 1 },
  { x: 1, y: 1 },
];
const sub2 = [
  { x: 0, y: 0, h: 2 },
  { x: 1, y: 1, w: 2 },
];

// Initialize sub-grid options
sub1.forEach((d) => (d.content = String(count++)));
sub2.forEach((d) => (d.content = String(count++)));

const subOptions = {
  cellHeight: 50,
  column: 'auto',
  acceptWidgets: true,
  subdGridDynamic: true,
  margin: 5,
  float: true,
  removable: '.trash',
};

// Main grid options
const options = {
  cellHeight: 50,
  margin: 5,
  minRow: 15,
  acceptWidgets: true,
  subdGridDynamic: true,
  float: true,
  id: 'main',
  removable: '.trash',
  subGridOpts: subOptions,
  children: [
    { x: 0, y: 0, content: 'regular item' },
    {
      x: 1,
      y: 0,
      w: 4,
      h: 4,
      sizeToContent: true,
      subGridOpts: { children: sub1, id: 'sub1_grid', class: 'sub1' },
    },
    {
      x: 5,
      y: 0,
      w: 3,
      h: 4,
      subGridOpts: { children: sub2, id: 'sub2_grid', class: 'sub2' },
    },
  ],
};

// Initialize the main grid
export function initializeGrid(containerSelector) {
  const grid = GridStack.addGrid(document.querySelector(containerSelector), options);
  setupEventListeners(grid);
  
  // Add dropped event listener
  grid.on('dropped', function(event, previousWidget, newWidget) {
    console.log('Item dropped into grid');
    const gridItemId = newWidget.el.getAttribute('gs-id');
    console.log('New widget ID:', gridItemId);

    // Find the sidebar element
    const sidebarElement = document.querySelector('.sidebar .grid-stack-item[gs-id="' + gridItemId + '"]');
    console.log('Sidebar element found:', sidebarElement);

    if (sidebarElement) {
      // Only modify the sidebar element
      sidebarElement.setAttribute('gs-id', 'random');
      console.log('Modified sidebar element gs-id to random');
    }
  });

  return grid;
}

function setupEventListeners(grid) {
  const saveBtn = document.getElementById('save-btn');
  const destroyBtn = document.getElementById('destroy-btn');
  const createBtn = document.getElementById('create-btn');

  const saveListBtn = document.getElementById('save-list-btn');
  const saveNoContentBtn = document.getElementById('save-no-content-btn');
  const clearBtn = document.getElementById('clear-btn');
  const loadBtn = document.getElementById('load-btn');

  if (saveBtn) {
    saveBtn.addEventListener('click', () => save(grid));
  }
  if (destroyBtn) {
    destroyBtn.addEventListener('click', () => destroy(grid));
  }
  if (createBtn) {
    createBtn.addEventListener('click', () => load(grid));
  }

  if (saveListBtn) {
    saveListBtn.addEventListener('click', () => save(grid, true, false));
  }
  if (saveNoContentBtn) {
    saveNoContentBtn.addEventListener('click', () => save(grid, false, false));
  }
  if (clearBtn) {
    clearBtn.addEventListener('click', () => destroy(grid, false));
  }
  if (loadBtn) {
    loadBtn.addEventListener('click', () => load(grid, false));
  }
}

// Add a widget to the main grid
export function addWidget(grid) {
  const uniqueId = generateUniqueId();
  grid.addWidget({
    x: Math.floor(Math.random() * 10),
    y: Math.floor(Math.random() * 10),
    content: `<div contentEditable="true" id="${uniqueId}">
      <button class="chuncky-btn" onClick="grid.removeWidget(this.parentNode.parentNode)">X</button>
      <button class="chuncky-btn">id: ${uniqueId}</button>
      Widget
    </div>`,
  });
  console.log(`Added element ID: ${uniqueId}`);
}

// Add a nested widget
export function addNested(grid) {
  const uniqueId = generateUniqueId('nested');
  grid.addWidget({
    x: Math.floor(Math.random() * 10),
    y: Math.floor(Math.random() * 10),
    subGridOpts: {
      children: [
        { content: `<div contentEditable="true" id="${uniqueId}">
          <button class="chuncky-btn" onClick="grid.removeWidget(this.parentNode.parentNode)">X</button>
          <button class="chuncky-btn">id: ${uniqueId}</button>
          Nested 1
        </div>` },
      ],
      ...subOptions,
    },
  });
  console.log(`Added element ID within nest: ${uniqueId}`);
}

// Add a widget to a sub-grid
export function addNewWidget(subGridSelector) {
  const subGrid = document.querySelector(subGridSelector).gridstack;
  const uniqueId = generateUniqueId('sub');
  subGrid.addWidget({
    x: Math.round(6 * Math.random()),
    y: Math.round(5 * Math.random()),
    w: Math.round(1 + 1 * Math.random()),
    h: Math.round(1 + 1 * Math.random()),
    content: `<div contentEditable="true" id="${uniqueId}">
      <button class="chuncky-btn" onClick="grid.removeWidget(this.parentNode.parentNode)">X</button>
      <button class="chuncky-btn">id: ${uniqueId}</button>
      ${String(count++)}
    </div>`,
  });
  console.log(`Cloned element ID: ${uniqueId}`);
}

// Save grid state
export function save(grid, content = true, full = true) {
  const savedOptions = grid.save(content, full);
  console.log(savedOptions);
  return savedOptions;
}

// Destroy the grid
export function destroy(grid, full = true) {
  if (full) {
    grid.off('dropped');
    grid.destroy();
    widgetIds = []; // Clear all IDs when grid is destroyed
  } else {
    grid.removeAll();
    widgetIds = []; // Clear all IDs when all widgets are removed
  }
}

// Reload the grid
export function load(grid, full = true) {
  if (full) {
    grid = GridStack.addGrid(document.querySelector('.container-fluid'), options);
  } else {
    grid.load(options);
  }
}

// Add function to remove ID from list when widget is removed
function removeWidgetId(id) {
  const index = widgetIds.indexOf(id);
  if (index > -1) {
    widgetIds.splice(index, 1);
  }
}

// Export the widget IDs list if needed
export function getWidgetIds() {
  return widgetIds;
}

// Add this new function near the top with other utility functions
function handleDragComplete(event) {
  //console.log('handledragcomplete');
  const gridItem = event.target;
  const gridItemId = gridItem.getAttribute('gs-id');
  console.log('Grid item ID:', gridItemId);

  // Find the sidebar element
  const sidebarElement = document.querySelector('.sidebar .grid-stack-item[gs-id="' + gridItemId + '"]');
  console.log('Sidebar element found:', sidebarElement);

  if (sidebarElement) {
    // Only modify the sidebar element
    sidebarElement.setAttribute('gs-id', 'random');
    console.log('Modified sidebar element gs-id to random');
  }
}

// Modify the setupDragIn function
export function setupDragIn(selector) {
  //console.log('setupdragin');
  GridStack.setupDragIn(selector, {
    appendTo: 'body',
    helper: function (event) {
      const uniqueId = generateUniqueId('drag');
      const target = event.target;
      const correctTarget = target.parentElement.classList.contains('grid-stack-item-content')
        ? target.parentElement.parentElement
        : target.parentElement;
      correctTarget.setAttribute('gs-id', uniqueId);
      
      const content = correctTarget.querySelector('.grid-stack-item-content');
      const id_box = correctTarget.querySelector('.grid-stack-item-id');
      
      const originalContent = content.innerHTML;
      
      id_box.innerHTML = `id: ${uniqueId}`
      
      const clone = GridStack.Utils.cloneNode(correctTarget);
      return clone;
    },
  });
}

function createWidget(widgetDefinition) {
  const grid = initializeGrid('.container-fluid'); // Ensure you have the grid initialized
  const uniqueId = generateUniqueId(); // Function to generate a unique ID for the widget

  // Create a new grid item
  const widgetContent = `
    <div id="${uniqueId}" class="widget-content">
      <canvas id="chart-${uniqueId}"></canvas>
    </div>
  `;

  grid.addWidget({
    x: Math.floor(Math.random() * 10),
    y: Math.floor(Math.random() * 10),
    content: widgetContent,
  });

  // Initialize the chart with the widget definition
  const ctx = document.getElementById(`chart-${uniqueId}`).getContext('2d');
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [], // Populate with your data
      datasets: [{
        label: 'My Dataset',
        data: [], // Populate with your data
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  // Subscribe to data updates if needed
  if (widgetDefinition.subscribe) {
    widgetDefinition.subscribe(data => {
      // Update the chart data here
      chart.data.labels.push(data.label);
      chart.data.datasets[0].data.push(data.value);
      chart.update();
    });
  }
}

// Example of a user-defined AriesMod (lineChart.js)
function lineChart() {
  return {
    subscribe: function(callback) {
      // Simulate data subscription
      setInterval(() => {
        const data = {
          label: new Date().toLocaleTimeString(),
          value: Math.random() * 100, // Random data for demonstration
        };
        callback(data);
      }, 1000);
    },
  };
}

function updateConfiguratorUI() {
  const configuratorContainer = document.getElementById('widget-configurator'); // Ensure this ID matches your configurator's container
  configuratorContainer.innerHTML = ''; // Clear existing content

  availableWidgets.forEach(widgetName => {
    const widgetItem = document.createElement('div');
    widgetItem.className = 'widget-item';
    widgetItem.innerHTML = `
      <h3>${widgetName}</h3>
      <button class="add-widget-btn" onclick="addWidgetToGrid('${widgetName}')">Add to Grid</button>
    `;
    configuratorContainer.appendChild(widgetItem);
  });
}

function addWidgetToGrid(widgetName) {
  // Assuming the widget definition is stored in a global object or can be retrieved
  const widgetDefinition = getWidgetDefinition(widgetName); // Implement this function to retrieve the widget definition
  createWidget(widgetDefinition);
}

const widgetDefinitions = {
  lineChart: lineChart, // Assuming lineChart is defined elsewhere
  // Add more widgets as needed
};

function getWidgetDefinition(widgetName) {
  return widgetDefinitions[widgetName] || null;
}


console.log('GridManager loaded');

function AttachStreamView(gridId, streamId, widgetType) {
    const gridIdValue = typeof gridId === 'object' ? gridId.value : gridId;
    const streamIdValue = typeof streamId === 'object' ? streamId.value : streamId;
    const widgetTypeValue = widgetType?.value || widgetType || "GraphDisplay";

    console.log("Attaching stream view:", { gridId: gridIdValue, streamId: streamIdValue, widgetType: widgetTypeValue });

    const gridElement = document.querySelector(`[gs-id="${gridIdValue}"]`);
    if (!gridElement) {
        console.error(`Grid with gs-id "${gridIdValue}" not found`);
        return;
    }

    const contentDiv = gridElement.querySelector('.grid-stack-item-content');
    if (!contentDiv) {
        console.error('Grid item content div not found');
        return;
    }

    // Clear existing content
    contentDiv.innerHTML = '';
    const componentContainer = document.createElement('div');
    componentContainer.className = 'component-container';
    contentDiv.appendChild(componentContainer);

    // Mount React component dynamically
    const root = ReactDOM.createRoot(componentContainer);

    function renderComponent(Component) {
        root.render(React.createElement(Component, { streamId: streamIdValue }));
    }

    if (widgetTypeValue === "SensorDisplay") {
        renderComponent(window.SensorDisplay);
    } else if (widgetTypeValue === "GraphDisplay") {
        if (window.GraphDisplay) {
            renderComponent(window.GraphDisplay);
        } else {
            root.render(React.createElement('div', null, 'Loading graph component...'));
            const checkInterval = setInterval(() => {
                if (window.GraphDisplay) {
                    clearInterval(checkInterval);
                    renderComponent(window.GraphDisplay);
                }
            }, 100);
        }
    } else {
        root.render(React.createElement('div', null, `Unknown widget type: ${widgetTypeValue}`));
    }

    if (window.subscribeToStream) {
        const [moduleId, streamName] = streamIdValue.split('.');
        window.subscribeToStream(moduleId, streamName);
    }
}

window.AttachStreamView = AttachStreamView;