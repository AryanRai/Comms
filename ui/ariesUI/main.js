import { app, BrowserWindow } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';

// Replace __dirname with ES module equivalent
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Global variable for the loading screen
let loadingScreen;

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
  });
};

// Function to create the main window
function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1300,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'renderer.cjs'), // Optional: preload script for secure node integration
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: true,
    },
    show: false,
    alwaysOnTop: true, // Make the window always on top initially
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
    }, 10000); // Adjust this value as needed
  });
}

// Electron app lifecycle hooks
app.on('ready', () => {
  createLoadingScreen();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
