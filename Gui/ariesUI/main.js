const { app, BrowserWindow } = require('electron');
const path = require('path');


/// create a global var, wich will keep a reference to out loadingScreen window
let loadingScreen;
const createLoadingScreen = () => {
  /// create a browser window
  loadingScreen = new BrowserWindow({
    width: 300,
    height: 375,
    frame: false,
    alwaysOnTop: true,
    //disable scrollbars
    icon: path.join(__dirname, 'src', 'assets', 'branding', 'Comms.png'),
    scrollbars: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      webSecurity: false,
    }
  });
  loadingScreen.loadFile(path.join(__dirname, 'src', 'preloader.html'));
  loadingScreen.on('closed', () => (loadingScreen = null));
  loadingScreen.webContents.on('did-finish-load', () => {
    loadingScreen.show();
  });
};


function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1300,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'renderer.js'), // Optional: preload script for secure node integration
      nodeIntegration: true, // Allow Node.js in frontend
      contextIsolation: false,
      webSecurity: true,
      // Make sure you don't have any settings here that might disable animations
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
  mainWindow.loadFile('src/dashv1.html');

  // Add event listener for 'enter-full-screen' event
  mainWindow.on('enter-full-screen', () => {
    mainWindow.TitleBarStyle('hidden');
    console.log("Entering full screen mode");
  });

  // Add event listener for 'leave-full-screen' event to revert the change
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
    }, 10000); // Adjust this value (in milliseconds) to set a minimum display time for the loading screen
  });
}

app.on('ready', () => {
  createLoadingScreen();
  createWindow();
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
