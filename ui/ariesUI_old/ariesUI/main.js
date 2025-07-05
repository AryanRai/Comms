import { app, BrowserWindow, ipcMain } from 'electron'; // ipcMain already included in your imports
import path from 'path';
import { fileURLToPath } from 'url';

// Replace __dirname with ES module equivalent
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Global variables for windows and audio
let loadingScreen;
let mainWindow;

// Audio configuration
const audioFiles = {
  startup: path.join(__dirname, 'sounds', 'startup.wav'),
  click: path.join(__dirname, 'sounds', 'click.wav'),
  success: path.join(__dirname, 'sounds', 'success.wav'),
  negative: path.join(__dirname, 'sounds', 'negative.wav')
};

// Function to create the loading screen
const createLoadingScreen = () => {
  loadingScreen = new BrowserWindow({
    width: 300,
    height: 375,
    frame: false,
    alwaysOnTop: true,
    icon: path.join(__dirname, 'src', 'assets', 'branding', 'Comms.png'),
    scrollbars: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      webSecurity: false,
    },
  });

  loadingScreen.loadFile(path.join(__dirname, 'src', 'preloader.html'));
  loadingScreen.on('closed', () => (loadingScreen = null));
  loadingScreen.webContents.on('did-finish-load', () => {
    loadingScreen.show();
    // Send audio paths to loading screen if needed
    loadingScreen.webContents.send('audio-config', audioFiles);
  });
};

// Function to create the main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1300,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'renderer.cjs'),
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: true,
    },
    show: false,
    alwaysOnTop: true,
    icon: path.join(__dirname, 'src', 'assets', 'branding', 'Comms.png'),
    titleBarOverlay: {
      color: '#2f323a',
      symbolColor: 'white',
      height: 22,
    },
  });

  mainWindow.setBackgroundMaterial("acrylic");
  mainWindow.loadFile('src/ariesUI.html');

  // Add event listeners for full-screen mode
  mainWindow.on('enter-full-screen', () => {
    mainWindow.TitleBarStyle('hidden');
    console.log("Entering full screen mode");
  });

  mainWindow.on('leave-full-screen', () => {
    mainWindow.TitleBarStyle('default');
    console.log("Leaving full screen mode");
  });

  mainWindow.webContents.on('did-finish-load', () => {
    // Send audio configuration to renderer
    mainWindow.webContents.send('audio-config', audioFiles);
    setTimeout(() => {
      // Play startup sound when main window loads
      mainWindow.webContents.send('play-audio', 'startup');
    }, 900);

    setTimeout(() => {
      if (loadingScreen) {
        loadingScreen.close();
      }
      mainWindow.show();
      mainWindow.focus();
      // Disable alwaysOnTop after a short delay
      setTimeout(() => {
        mainWindow.setAlwaysOnTop(false);
      }, 1000);
    }, 3000); // Adjust this value as needed
  });
}

// Function to initialize IPC for audio control
function setupAudioIPC() {
  ipcMain.on('play-audio', (event, soundKey) => {
    console.log(`Requested to play: ${soundKey}`);
  });

  ipcMain.on('audio-error', (event, error) => {
    console.error('Audio error:', error);
  });
}

function setupPerformaceIPC() {
  // Handle IPC request for performance metrics
  ipcMain.on('get-performance-metrics', (event) => {
    const cpuUsage = process.getCPUUsage().percentCPUUsage * 100; // Percentage
    const memoryUsage = (process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2); // MB
    event.reply('performance-metrics', { cpuUsage, memoryUsage });
  });
  }

// Electron app lifecycle hooks
app.on('ready', () => {
  setupAudioIPC();
  setupPerformaceIPC(); // Fixed typo from 'setupPerformaceIPC' to 'setupPerformanceIPC'
  createLoadingScreen();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});