const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');

let win;
let tray;

function createWindow() {
  win = new BrowserWindow({
    width: 1200,
    height: 800,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true, // Hide from taskbar
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }
  });

  // Enable click-through for transparent areas initially
  win.setIgnoreMouseEvents(true, { forward: true });

  win.loadFile('index.html');
}

const fs = require('fs');

function createTray() {
  const iconPath = path.join(__dirname, 'icon.png');
  
  try {
    tray = new Tray(iconPath);
    
    const contextMenu = Menu.buildFromTemplate([
      { label: 'Show JARVIS', click: () => win.show() },
      { label: 'Hide JARVIS', click: () => win.hide() },
      { type: 'separator' },
      { label: 'Exit', click: () => {
        app.isQuitting = true;
        app.quit();
      }}
    ]);

    tray.setToolTip('J.A.R.V.I.S. Core');
    tray.setContextMenu(contextMenu);

    tray.on('click', () => {
      win.isVisible() ? win.hide() : win.show();
    });
  } catch (e) {
    console.error("[!] Failed to create tray:", e);
  }
}

ipcMain.on('set-ignore-mouse-events', (event, ignore, options) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (win) win.setIgnoreMouseEvents(ignore, options);
});

ipcMain.on('resize-window', (event, width, height) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (win) {
    win.setSize(width, height);
    // Optional: Reposition to corner?
    // win.setPosition(screen.getPrimaryDisplay().workArea.width - width, screen.getPrimaryDisplay().workArea.height - height);
  }
});

ipcMain.on('quit-app', () => {
  app.quit();
});

app.whenReady().then(() => {
  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
