const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
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
    alwaysOnTop: false,
    skipTaskbar: false, // Show in taskbar
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

let updateProcess = null;

// Helper to run a command and return a Promise
function runCommandPromise(cmd, cwd) {
  return new Promise((resolve) => {
    exec(cmd, { cwd }, (err, stdout, stderr) => {
      resolve({ success: !err, stdout: stdout || '', stderr: stderr || '' });
    });
  });
}

// Check if update is available
async function isUpdateAvailable() {
  const repoPath = path.join(__dirname, '..', 'Github', 'J.A.R.V.I.S.-AI-Assistant');
  if (!fs.existsSync(repoPath)) {
    console.log("[*] GitHub repository not found at:", repoPath);
    return false;
  }

  console.log("[*] Fetching latest updates from GitHub...");
  const fetchRes = await runCommandPromise('git fetch', repoPath);
  if (!fetchRes.success) {
    console.log("[WARN] Failed to fetch updates (offline or git error). Skipping update check.");
    return false;
  }

  const diffRes = await runCommandPromise('git rev-list --count HEAD..origin/main', repoPath);
  if (!diffRes.success) {
    console.error("Failed to compare HEAD with origin/main.");
    return false;
  }

  const count = parseInt(diffRes.stdout.trim(), 10);
  return count > 0;
}

// Run updater.py using venv python
function runUpdater() {
  return new Promise((resolve) => {
    const pythonPath = path.join(__dirname, '..', 'venv', 'Scripts', 'python.exe');
    const updaterPath = path.join(__dirname, '..', 'updater.py');
    
    if (!fs.existsSync(pythonPath) || !fs.existsSync(updaterPath)) {
      resolve({ success: false, message: 'Python virtual env or updater.py not found.' });
      return;
    }

    const updater = spawn(pythonPath, [updaterPath]);
    
    let output = '';
    updater.stdout.on('data', (data) => {
      output += data.toString();
      const lines = data.toString().split('\n');
      for (let line of lines) {
        if (line.trim().startsWith('[*]') || line.trim().startsWith('[OK]')) {
          if (win) win.webContents.send('update-status', line.trim());
          console.log(`[Updater]: ${line.trim()}`);
        }
      }
    });

    updater.stderr.on('data', (data) => {
      console.error(`[Updater Error]: ${data}`);
    });

    updater.on('close', (code) => {
      resolve({ success: code === 0, message: output });
    });
  });
}

ipcMain.handle('perform-update', async (event) => {
  const baseDir = path.join(__dirname, '..');
  const updaterScript = path.join(baseDir, 'updater.py');
  
  if (!fs.existsSync(updaterScript)) {
    console.error("[!] Updater script not found:", updaterScript);
    if (win) win.webContents.send('update-status', 'Updater script not found');
    return false;
  }

  console.log("[*] Starting update process...");
  
  try {
    // Show update overlay
    if (win) {
      win.webContents.send('show-update-overlay', 'Checking for updates...');
    }

    // Run the updater script
    updateProcess = spawn('python', [updaterScript], {
      cwd: baseDir,
      windowsHide: true
    });

    let updateCompleted = false;
    let updateFailed = false;
    let alreadyUpToDate = false;
    let allOutput = ''; // Accumulate all output for better parsing

    updateProcess.stdout.on('data', (data) => {
      const output = data.toString();
      allOutput += output; // Accumulate all output
      console.log(`[Updater]: ${output}`);
      
      // Parse output and send status updates
      if (output.includes('Checking')) {
        if (win) win.webContents.send('update-status', 'Checking for updates...');
      } else if (output.includes('Backup')) {
        if (win) win.webContents.send('update-status', 'Creating backup...');
      } else if (output.includes('Git pull')) {
        if (win) win.webContents.send('update-status', 'Fetching latest changes...');
      } else if (output.includes('Synchronizing')) {
        if (win) win.webContents.send('update-status', 'Synchronizing files...');
      } else if (output.includes('dependencies')) {
        if (win) win.webContents.send('update-status', 'Updating dependencies...');
      } else if (output.includes('Already up to date') || output.includes('already up to date')) {
        if (win) win.webContents.send('update-status', 'Already up to date! No restart needed.');
        updateCompleted = true;
        alreadyUpToDate = true;
      } else if (output.includes('complete') || output.includes('successfully') || output.includes('updated successfully')) {
        if (win) win.webContents.send('update-status', 'Update complete! Restarting...');
        updateCompleted = true;
      } else if (output.includes('[OK]') && (output.includes('Update marked as complete') || output.includes('updated successfully'))) {
        if (win) win.webContents.send('update-status', 'Update complete! Restarting...');
        updateCompleted = true;
      } else if (output.includes('ERROR') || output.includes('[!]')) {
        // Only treat as failure if it's an actual error (marked with ERROR or [!])
        updateFailed = true;
      }
      // Ignore WARN messages - they're not failures
    });

    updateProcess.stderr.on('data', (data) => {
      const errorOutput = data.toString();
      console.error(`[Updater Error]: ${errorOutput}`);
      // Don't immediately mark as failed - some warnings go to stderr
      // Only mark as failed if it's a real error
      if (errorOutput.includes('ERROR') || errorOutput.includes('Error') || errorOutput.includes('Failed')) {
        updateFailed = true;
      }
    });

    return new Promise((resolve) => {
      updateProcess.on('close', (code) => {
        console.log(`[Updater] exited with code ${code}`);
        console.log(`[Updater] Full output: ${allOutput}`);
        updateProcess = null;
        
        // More robust success detection:
        // 1. Exit code must be 0
        // 2. Either updateCompleted flag is set OR output contains success indicators
        // 3. No explicit failures detected
        const hasSuccessIndicators = allOutput.includes('Already up to date') || 
                                      allOutput.includes('updated successfully') ||
                                      allOutput.includes('Update marked as complete') ||
                                      allOutput.includes('J.A.R.V.I.S. updated successfully');
        
        const isSuccessful = code === 0 && !updateFailed && (updateCompleted || hasSuccessIndicators);
        
        if (isSuccessful) {
          if (win) {
            const isUpToDate = alreadyUpToDate || allOutput.includes('Already up to date') || allOutput.includes('Already up-to-date');
            if (isUpToDate) {
              win.webContents.send('update-success', 'System is already up to date. No updates needed.');
            } else {
              win.webContents.send('update-success', 'Update complete! Restarting J.A.R.V.I.S. system...');
              setTimeout(() => {
                app.relaunch();
                app.exit();
              }, 2500);
            }
          }
          resolve(true);
        } else {
          if (win) {
            const errorLines = allOutput.split('\n').filter(l => l.toLowerCase().includes('failed') || l.includes('ERROR') || l.includes('[!]'));
            const descriptiveError = errorLines.length > 0 ? errorLines[errorLines.length - 1].trim() : 'Unknown error occurred during installation.';
            win.webContents.send('update-error', descriptiveError);
          }
          resolve(false);
        }
      });
    });

  } catch (error) {
    console.error("[!] Update process error:", error);
    if (win) {
      win.webContents.send('update-error', 'Update failed: ' + error.message);
    }
    return false;
  }
});

ipcMain.on('cancel-update', () => {
  if (updateProcess) {
    console.log("[*] Cancelling update process...");
    try {
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', updateProcess.pid, '/f', '/t']);
      } else {
        updateProcess.kill();
      }
      updateProcess = null;
    } catch (err) {
      console.error("Failed to cancel update:", err);
    }
  }
  
  if (win) {
    win.webContents.send('hide-update-overlay');
  }
});

function syncStoreToEnv() {
  const groqKey = store.get('groqKey') || '';
  const geminiKey = store.get('geminiKey') || '';
  
  if (!groqKey && !geminiKey) return; // No keys saved in Store to sync

  const envPath = path.join(__dirname, '..', '.env');
  try {
    let envContent = '';
    let needsUpdate = false;
    
    if (fs.existsSync(envPath)) {
      envContent = fs.readFileSync(envPath, 'utf8');
      
      const groqMatch = envContent.match(/GROQ_API_KEY\s*=\s*["']?([^"'\r\n]*)["']?/);
      const geminiMatch = envContent.match(/GOOGLE_API_KEY\s*=\s*["']?([^"'\r\n]*)["']?/);
      
      const currentGroq = groqMatch ? groqMatch[1] : '';
      const currentGemini = geminiMatch ? geminiMatch[1] : '';
      
      if (groqKey && currentGroq !== groqKey) needsUpdate = true;
      if (geminiKey && currentGemini !== geminiKey) needsUpdate = true;
    } else {
      needsUpdate = true;
      const examplePath = path.join(__dirname, '..', '.env.example');
      if (fs.existsSync(examplePath)) {
        envContent = fs.readFileSync(examplePath, 'utf8');
      }
    }

    if (needsUpdate) {
      if (envContent.includes('GROQ_API_KEY')) {
        envContent = envContent.replace(/GROQ_API_KEY\s*=\s*["']?[^"'\r\n]*["']?/, `GROQ_API_KEY="${groqKey}"`);
      } else {
        envContent += `\nGROQ_API_KEY="${groqKey}"`;
      }

      if (envContent.includes('GOOGLE_API_KEY')) {
        envContent = envContent.replace(/GOOGLE_API_KEY\s*=\s*["']?[^"'\r\n]*["']?/, `GOOGLE_API_KEY="${geminiKey}"`);
      } else {
        envContent += `\nGOOGLE_API_KEY="${geminiKey}"`;
      }

      fs.writeFileSync(envPath, envContent.trim() + '\n', 'utf8');
      console.log("[*] API keys auto-synced from Store to .env on startup.");
    }
  } catch (e) {
    console.error("Failed to auto-sync keys to .env file:", e);
  }
}

app.whenReady().then(() => {
  syncStoreToEnv();
  createWindow();
  createTray();

  // Wait for window to load its DOM before starting auto-update check
  win.webContents.once('did-finish-load', async () => {
    const updateAvailable = await isUpdateAvailable();
    if (updateAvailable) {
      console.log("[*] System updates available. Triggering auto-update...");
      win.webContents.send('show-update-overlay', 'System update detected. Downloading latest changes...');
      
      // Perform the update
      const res = await runUpdater();
      if (res.success) {
        win.webContents.send('update-success', 'Auto-update complete! Restarting system...');
        setTimeout(() => {
          app.relaunch();
          app.exit();
        }, 2500);
      } else {
        const errorLines = res.message.split('\n').filter(l => l.toLowerCase().includes('failed') || l.includes('ERROR') || l.includes('[!]'));
        const descriptiveError = errorLines.length > 0 ? errorLines[errorLines.length - 1].trim() : 'Unknown error occurred.';
        win.webContents.send('update-error', `Auto-update failed: ${descriptiveError}`);
        setTimeout(() => {
          win.webContents.send('hide-update-overlay');
          startBackend();
        }, 4000);
      }
    } else {
      console.log("[*] System is up-to-date. Starting backend...");
      startBackend();
    }
  });

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
