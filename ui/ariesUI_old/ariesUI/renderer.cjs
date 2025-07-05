
// renderer.cjs
const { ipcRenderer } = require('electron');

let audioFiles = {};

ipcRenderer.on('audio-config', (event, files) => {
  audioFiles = files;
});

ipcRenderer.on('play-audio', (event, soundKey) => {
  if (audioFiles[soundKey]) {
    const audio = new Audio(audioFiles[soundKey]);
    audio.play().catch(error => {
      ipcRenderer.send('audio-error', error.message);
    });
  }
});

// Export function to play sounds from React components
module.exports = {
  playSound: (soundKey) => {
    if (audioFiles[soundKey]) {
      const audio = new Audio(audioFiles[soundKey]);
      audio.play().catch(error => {
        ipcRenderer.send('audio-error', error.message);
      });
    }
  }
};