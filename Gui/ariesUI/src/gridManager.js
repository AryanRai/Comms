// Global variables
let count = 0;
let gridItemCounter = 0;

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

  return grid;
}

// Add a widget to the main grid
export function addWidget(grid) {
  const uniqueId = `widget-${gridItemCounter++}`;
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
  const uniqueId = `nested-widget-${gridItemCounter++}`;
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
  const uniqueId = `sub-widget-${gridItemCounter++}`;
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
  } else {
    grid.removeAll();
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

// Setup drag-in behavior
export function setupDragIn(selector) {
  GridStack.setupDragIn(selector, {
    appendTo: 'body',
    helper: function (event) {
      const uniqueId = `id-${Math.random().toString(36).substr(2, 9)}`;
      const target = event.target;
      const correctTarget = target.parentElement.classList.contains('grid-stack-item-content')
        ? target.parentElement.parentElement
        : target.parentElement;
      correctTarget.setAttribute('gs-id', uniqueId);
      
      // Add ID display to the content
      const content = correctTarget.querySelector('.grid-stack-item-content');
      if (content) {
        const originalContent = content.innerHTML;
        content.innerHTML = `
          <button class="chuncky-btn" onClick="grid.removeWidget(this.parentNode.parentNode)">X</button>
          <button class="chuncky-btn">id: ${uniqueId}</button>
          ${originalContent}
        `;
      }
      
      const clone = GridStack.Utils.cloneNode(correctTarget);
      return clone;
    },
  });
}
