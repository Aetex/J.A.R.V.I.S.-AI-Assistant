const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');
const fs = require('fs');

const store = new Store();
let win;
let tray;
let backendProcess = null;

// Function to start the bundled Python backend
function startBackend() {
  if (!app.isPackaged) return; // Only start in packaged mode

  let groqKey = store.get('groqKey');
  let geminiKey = store.get('geminiKey');

  // Fallback to .env in packaged mode if store is empty
  if (!groqKey && !geminiKey) {
    const envPath = path.join(__dirname, '..', '.env');
    if (fs.existsSync(envPath)) {
      try {
        const envContent = fs.readFileSync(envPath, 'utf8');
        const groqMatch = envContent.match(/GROQ_API_KEY\s*=\s*["']?([^"'\r\n]+)["']?/);
        const geminiMatch = envContent.match(/GOOGLE_API_KEY\s*=\s*["']?([^"'\r\n]+)["']?/);
        if (groqMatch) groqKey = groqMatch[1];
        if (geminiMatch) geminiKey = geminiMatch[1];
      } catch (e) {
        console.error("Failed to read fallback .env file:", e);
      }
    }
  }

  // If no keys, don't start backend yet, wait for UI to provide them
  if (!groqKey && !geminiKey) {
    console.log("[*] No API keys found. Waiting for First-Time Setup...");
    return;
  }

  const backendPath = path.join(process.resourcesPath, 'assets', 'backend', 'backend.exe');
  
  if (!fs.existsSync(backendPath)) {
    console.error("[!] Bundled backend.exe not found at:", backendPath);
    return;
  }

  console.log("[*] Starting bundled backend...");
  
  const args = [];
  if (groqKey) args.push('--groq', groqKey);
  if (geminiKey) args.push('--gemini', geminiKey);

  backendProcess = spawn(backendPath, args);

  backendProcess.stdout.on('data', (data) => {
    console.log(`[Backend]: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`[Backend Error]: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`[Backend] exited with code ${code}`);
  });
}

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

function createTray() {
  const iconPath = path.join(__dirname, 'icon.png');
  
  if (!fs.existsSync(iconPath)) {
    console.log("[*] Tray icon not found. Skipping tray initialization to prevent crash.");
    return;
  }

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

// IPC handlers for API Keys
ipcMain.handle('check-api-keys', () => {
  let groqKey = store.get('groqKey') || '';
  let geminiKey = store.get('geminiKey') || '';
  
  // Fallback to reading from .env in the parent directory
  if (!groqKey && !geminiKey) {
    const envPath = path.join(__dirname, '..', '.env');
    if (fs.existsSync(envPath)) {
      try {
        const envContent = fs.readFileSync(envPath, 'utf8');
        const groqMatch = envContent.match(/GROQ_API_KEY\s*=\s*["']?([^"'\r\n]+)["']?/);
        const geminiMatch = envContent.match(/GOOGLE_API_KEY\s*=\s*["']?([^"'\r\n]+)["']?/);
        if (groqMatch) groqKey = groqMatch[1];
        if (geminiMatch) geminiKey = geminiMatch[1];
      } catch (e) {
        console.error("Failed to read .env file:", e);
      }
    }
  }
  
  return {
    isPackaged: app.isPackaged,
    hasKeys: !!(groqKey || geminiKey),
    groqKey: groqKey,
    geminiKey: geminiKey
  };
});

ipcMain.on('save-api-keys', (event, keys) => {
  store.set('groqKey', keys.groq);
  store.set('geminiKey', keys.gemini);
  
  console.log("[*] API keys saved successfully to Electron Store.");

  // Write/Update the .env file in parent directory
  const envPath = path.join(__dirname, '..', '.env');
  try {
    let envContent = '';
    if (fs.existsSync(envPath)) {
      envContent = fs.readFileSync(envPath, 'utf8');
    } else {
      const examplePath = path.join(__dirname, '..', '.env.example');
      if (fs.existsSync(examplePath)) {
        envContent = fs.readFileSync(examplePath, 'utf8');
      }
    }

    if (envContent.includes('GROQ_API_KEY')) {
      envContent = envContent.replace(/GROQ_API_KEY\s*=\s*["']?[^"'\r\n]*["']?/, `GROQ_API_KEY="${keys.groq}"`);
    } else {
      envContent += `\nGROQ_API_KEY="${keys.groq}"`;
    }

    if (envContent.includes('GOOGLE_API_KEY')) {
      envContent = envContent.replace(/GOOGLE_API_KEY\s*=\s*["']?[^"'\r\n]*["']?/, `GOOGLE_API_KEY="${keys.gemini}"`);
    } else {
      envContent += `\nGOOGLE_API_KEY="${keys.gemini}"`;
    }

    fs.writeFileSync(envPath, envContent.trim() + '\n', 'utf8');
    console.log("[*] API keys synced to .env file successfully.");
  } catch (e) {
    console.error("Failed to sync keys to .env file:", e);
  }
  
  // Terminate old backend process to reload new keys (packaged mode)
  if (backendProcess) {
    console.log("[*] Terminating old backend process to apply new keys...");
    try {
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', backendProcess.pid, '/f', '/t']);
      } else {
        backendProcess.kill();
      }
    } catch (err) {
      console.error("Failed to terminate old backend:", err);
    }
    backendProcess = null;
  }
  
  // Re-start the backend with the new keys
  startBackend();
});

app.whenReady().then(() => {
  createWindow();
  createTray();
  startBackend();

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

app.on('will-quit', () => {
  if (backendProcess) {
    console.log("[*] Terminating bundled backend process...");
    // Force kill the child process on Windows
    spawn('taskkill', ['/pid', backendProcess.pid, '/f', '/t']);
  }
});
