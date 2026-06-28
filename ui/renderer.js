const { ipcRenderer } = require('electron');

const input = document.getElementById('user-input');
const chatLog = document.getElementById('chat-log');
const micBtn = document.getElementById('mic-btn');
const core = document.getElementById('jarvis-core');
const innerCore = core.querySelector('.inner-core');

const cpuBar = document.getElementById('cpu-bar');
const memBar = document.getElementById('mem-bar');
const volBar = document.getElementById('vol-bar');
const cpuVal = document.getElementById('cpu-val');
const memVal = document.getElementById('mem-val');
const volVal = document.getElementById('vol-val');

const BACKEND_URL = 'http://127.0.0.1:8000';

// State tracking
let isResponding = false;

function setCoreListen(responding) {
    isResponding = responding;
    if (responding) {
        core.classList.remove('idle');
        core.classList.add('responding');
        if (innerCore) {
            innerCore.classList.remove('idle');
            innerCore.classList.add('responding');
        }
    } else {
        core.classList.remove('responding');
        core.classList.add('idle');
        if (innerCore) {
            innerCore.classList.remove('responding');
            innerCore.classList.add('idle');
        }
    }
}

function addMessage(text, sender, isHTML = false) {
    const div = document.createElement('div');
    div.className = `msg msg-${sender}`;
    if (isHTML) {
        div.innerHTML = sender === 'jarvis' ? `> ${text}` : `[USER]: ${text}`;
    } else {
        div.innerText = sender === 'jarvis' ? `> ${text}` : `[USER]: ${text}`;
    }
    
    // Smooth scroll animation
    div.style.opacity = '0';
    div.style.transform = 'translateY(10px)';
    
    chatLog.appendChild(div);
    
    // Trigger animation
    requestAnimationFrame(() => {
        div.style.transition = 'all 0.4s ease';
        div.style.opacity = '1';
        div.style.transform = 'translateY(0)';
    });
    
    chatLog.scrollTop = chatLog.scrollHeight;
}

async function stopSpeech() {
    try {
        await fetch(`${BACKEND_URL}/stop`, { method: 'POST' });
    } catch (e) { console.error("Failed to stop speech"); }
}

function handleJarvisResponse(data) {
    if (!data) return;
    
    if (data.response) {
        addMessage(data.response, 'jarvis');
    }
    
    // Check for shutdown tool call
    if (data.tools_executed && data.tools_executed.some(t => t.name === 'shutdown_system')) {
        console.log("[*] Shutdown tool detected. Closing GUI immediately...");
        setTimeout(() => {
            ipcRenderer.send('quit-app');
        }, 500);
    }

    if (data.tools_executed && data.tools_executed.length > 0) {
        data.tools_executed.forEach(tool => {
            console.log(`Tool executed: ${tool.name} - ${tool.result}`);
        });
    }
}

async function sendMessage(msg) {
    if (!msg) return;
    
    await stopSpeech();
    addMessage(msg, 'user');
    setCoreListen(true);
    
    try {
        const res = await fetch(`${BACKEND_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });

        if (!res.ok) {
            const errorData = await res.json();
            addMessage(`Sir, my processors are reporting an error: ${errorData.detail || 'Internal Error'}`, 'jarvis');
            setCoreListen(false);
            return;
        }

        const data = await res.json();
        handleJarvisResponse(data);
        setCoreListen(false);
        
    } catch (error) {
        addMessage("I'm having trouble connecting to my core processors, sir. Please ensure the backend is running. <span id='open-keys-err' style='color: #00f6ff; text-decoration: underline; cursor: pointer; font-weight: bold;'>Configure API Keys</span>", 'jarvis', true);
        const errLink = document.getElementById('open-keys-err');
        if (errLink) {
            errLink.addEventListener('click', openSetupOverlay);
        }
        console.error(error);
        setCoreListen(false);
    }
}

async function updateStatus() {
    try {
        const res = await fetch(`${BACKEND_URL}/status`);
        const data = await res.json();
        
        // Smooth bar transitions with animation
        const updateBar = (bar, value, val, text) => {
            bar.style.transition = 'width 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            bar.style.width = `${value}%`;
            val.style.transition = 'all 0.3s ease';
            val.innerText = text;
        };
        
        updateBar(cpuBar, data.cpu, cpuVal, `${Math.round(data.cpu)}%`);
        updateBar(memBar, data.memory, memVal, `${Math.round(data.memory)}%`);
        updateBar(volBar, data.volume, volVal, `${data.volume}%`);
    } catch (e) {
        // Silently fail status updates if backend is down
    }
}

// Listeners
input.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter' && input.value.trim()) {
        const msg = input.value.trim();
        input.value = '';
        await sendMessage(msg);
    }
});

core.addEventListener('click', async () => {
    await stopSpeech();
    // Add click animation
    core.style.animation = 'none';
    setTimeout(() => {
        core.style.animation = '';
    }, 10);
});

// Hover effects on core
core.addEventListener('mouseenter', () => {
    core.style.filter = 'brightness(1.3)';
});

core.addEventListener('mouseleave', () => {
    core.style.filter = 'brightness(1)';
});

micBtn.addEventListener('click', async () => {
    micBtn.style.color = "red";
    micBtn.style.animation = 'none';
    micBtn.style.transition = 'all 0.2s ease';
    micBtn.style.transform = 'scale(1.2)';
    micBtn.innerText = "🔴";
    
    try {
        const res = await fetch(`${BACKEND_URL}/listen`);
        const data = await res.json();
        if (data.text) {
            await sendMessage(data.text);
        }
    } catch (e) {
        addMessage("Sir, I'm unable to access the microphone array.", 'jarvis');
    } finally {
        micBtn.style.color = "#00f6ff";
        micBtn.style.transform = 'scale(1)';
        micBtn.innerText = "🎙️";
    }
});

// Mic button hover effect
micBtn.addEventListener('mouseenter', () => {
    micBtn.style.transition = 'all 0.2s ease';
    micBtn.style.filter = 'drop-shadow(0 0 8px #00f6ff)';
});

micBtn.addEventListener('mouseleave', () => {
    micBtn.style.filter = 'drop-shadow(0 0 0px #00f6ff)';
});

// View Toggling
const miniToggle = document.getElementById('mini-toggle');
const exitBtn = document.getElementById('exit-btn');
const fullView = document.getElementById('full-view');
const miniView = document.getElementById('mini-view');
const miniCore = document.getElementById('mini-core');
let isMini = false;

exitBtn.addEventListener('click', async () => {
    addMessage("Shutting down all systems, sir.", 'jarvis');
    
    // Shutdown animation
    const container = document.getElementById('full-view');
    if (container) {
        container.style.transition = 'all 0.8s ease';
        container.style.opacity = '0';
        container.style.transform = 'scale(0.95)';
    }
    
    setTimeout(() => {
        try {
            // 1. Tell backend to shut down
            fetch(`${BACKEND_URL}/shutdown`, { method: 'POST' });
            // 2. Close UI immediately
            ipcRenderer.send('quit-app');
        } catch (e) {
            ipcRenderer.send('quit-app'); // Force close UI anyway
        }
    }, 600);
});

// Exit button hover effect
exitBtn.addEventListener('mouseenter', () => {
    exitBtn.style.transition = 'all 0.2s ease';
    exitBtn.style.boxShadow = '0 0 10px rgba(255, 68, 68, 0.5)';
    exitBtn.style.transform = 'scale(1.05)';
});

exitBtn.addEventListener('mouseleave', () => {
    exitBtn.style.boxShadow = 'none';
    exitBtn.style.transform = 'scale(1)';
});

function toggleView() {
    isMini = !isMini;
    document.body.classList.toggle('mini-mode');
    if (isMini) {
        fullView.style.display = 'none';
        miniView.style.display = 'flex';
        ipcRenderer.send('resize-window', 150, 150);
    } else {
        fullView.style.display = 'grid';
        miniView.style.display = 'none';
        ipcRenderer.send('resize-window', 1200, 800);
    }
}

miniToggle.addEventListener('click', toggleView);
miniCore.addEventListener('click', toggleView);

// EventSource for background events (Wake Word)
const eventSource = new EventSource(`${BACKEND_URL}/events`);

eventSource.addEventListener('wakeword', (e) => {
    const data = JSON.parse(e.data);
    console.log("Wake word detected!");
    setCoreListen(true);
    setTimeout(() => { setCoreListen(false); }, 1000);
});

eventSource.addEventListener('user_speech', (e) => {
    const data = JSON.parse(e.data);
    addMessage(data.text, 'user');
    setCoreListen(true);
});

eventSource.addEventListener('jarvis_response', (e) => {
    const data = JSON.parse(e.data);
    setCoreListen(true);
    handleJarvisResponse(data);
    setCoreListen(false);
});

// Click-through handling
window.addEventListener('mousemove', (event) => {
    if (event.target === document.documentElement || event.target === document.body) {
        ipcRenderer.send('set-ignore-mouse-events', true, { forward: true });
    } else {
        ipcRenderer.send('set-ignore-mouse-events', false);
    }
});

// First-Time Setup Logic
async function openSetupOverlay() {
    const status = await ipcRenderer.invoke('check-api-keys');
    
    // Pre-populate keys
    document.getElementById('gemini-key-input').value = status.geminiKey || '';
    document.getElementById('groq-key-input').value = status.groqKey || '';

    const cancelBtn = document.getElementById('cancel-keys-btn');
    const saveBtn = document.getElementById('save-keys-btn');

    if (status.hasKeys) {
        cancelBtn.style.display = 'block';
        saveBtn.innerText = 'UPDATE CORE';
    } else {
        cancelBtn.style.display = 'none';
        saveBtn.innerText = 'INITIALIZE';
    }

    document.getElementById('setup-overlay').style.display = 'flex';
}

async function checkSetup() {
    const status = await ipcRenderer.invoke('check-api-keys');
    if (!status.hasKeys) {
        openSetupOverlay();
    }
}

document.getElementById('save-keys-btn').addEventListener('click', () => {
    const geminiKey = document.getElementById('gemini-key-input').value.trim();
    const groqKey = document.getElementById('groq-key-input').value.trim();

    if (!geminiKey && !groqKey) {
        alert("Sir, you must provide at least one API key for me to function.");
        return;
    }

    ipcRenderer.send('save-api-keys', { gemini: geminiKey, groq: groqKey });
    document.getElementById('setup-overlay').style.display = 'none';
    
    // Attempt to connect to backend after a short delay to allow it to spin up
    setTimeout(updateStatus, 3000);
});

document.getElementById('cancel-keys-btn').addEventListener('click', () => {
    document.getElementById('setup-overlay').style.display = 'none';
});

// ── SETTINGS MODAL ────────────────────────────────────────────────────────
const settingsModal = document.getElementById('settings-modal');
const settingsBtn = document.getElementById('settings-btn');
const settingsCloseBtn = document.getElementById('settings-close-btn');
const settingsOverlay = document.querySelector('.settings-modal-overlay');

function openSettingsModal() {
    settingsModal.classList.remove('hidden');
}

function closeSettingsModal() {
    settingsModal.classList.add('hidden');
}

settingsBtn.addEventListener('click', openSettingsModal);
settingsCloseBtn.addEventListener('click', closeSettingsModal);
settingsOverlay.addEventListener('click', closeSettingsModal);

// Close modal when clicking outside the content
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal || e.target === settingsOverlay) {
        closeSettingsModal();
    }
});

// Key press to close modal (Escape)
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !settingsModal.classList.contains('hidden')) {
        closeSettingsModal();
    }
});

// ── UPDATE button (inside settings modal) ──────────────────────────────────
function resetUpdateUI() {
    const header = document.getElementById('update-header');
    const progressBar = document.getElementById('update-progress-bar');
    const cancelBtn = document.getElementById('cancel-update-btn');
    const dismissBtn = document.getElementById('dismiss-update-btn');
    
    header.textContent = 'SYSTEM UPDATE';
    header.style.color = '#00ff00'; 
    progressBar.style.width = '0%';
    progressBar.style.backgroundColor = '#00ff00'; 
    cancelBtn.style.display = 'inline-block';
    dismissBtn.style.display = 'none';
}

document.getElementById('update-btn').addEventListener('click', async () => {
    closeSettingsModal();
    const overlay = document.getElementById('update-overlay');
    const statusText = document.getElementById('update-status-text');
    const progressBar = document.getElementById('update-progress-bar');
    
    resetUpdateUI();
    overlay.style.display = 'flex';
    statusText.textContent = 'Initiating system update sequence...';
    progressBar.style.width = '10%';

    await ipcRenderer.invoke('perform-update');
});

// ── KEYS button (inside settings modal) ────────────────────────────────────
document.getElementById('keys-btn').addEventListener('click', () => {
    closeSettingsModal();
    openSetupOverlay();
});

document.getElementById('cancel-update-btn').addEventListener('click', () => {
    const overlay = document.getElementById('update-overlay');
    overlay.style.display = 'none';
    ipcRenderer.send('cancel-update');
});

document.getElementById('dismiss-update-btn').addEventListener('click', () => {
    const overlay = document.getElementById('update-overlay');
    overlay.style.display = 'none';
});

// ── Update overlay IPC events (from main.js) ───────────────────────────────
ipcRenderer.on('show-update-overlay', (event, message) => {
    const overlay = document.getElementById('update-overlay');
    const statusText = document.getElementById('update-status-text');
    const progressBar = document.getElementById('update-progress-bar');
    
    resetUpdateUI();
    overlay.style.display = 'flex';
    if (message) statusText.textContent = message;
    progressBar.style.width = '20%';
});

ipcRenderer.on('update-status', (event, message) => {
    const statusText = document.getElementById('update-status-text');
    const progressBar = document.getElementById('update-progress-bar');
    if (statusText && message) {
        statusText.textContent = message;
        // Update progress based on message content
        if (message.includes('Checking')) progressBar.style.width = '30%';
        else if (message.includes('Backup')) progressBar.style.width = '40%';
        else if (message.includes('Git')) progressBar.style.width = '50%';
        else if (message.includes('Synchronizing')) progressBar.style.width = '60%';
        else if (message.includes('dependencies')) progressBar.style.width = '75%';
        else if (message.includes('complete') || message.includes('success')) progressBar.style.width = '100%';
    }
});

ipcRenderer.on('update-progress', (event, progress) => {
    const progressBar = document.getElementById('update-progress-bar');
    if (progressBar) progressBar.style.width = `${progress}%`;
});

ipcRenderer.on('update-success', (event, message) => {
    const header = document.getElementById('update-header');
    const statusText = document.getElementById('update-status-text');
    const progressBar = document.getElementById('update-progress-bar');
    const cancelBtn = document.getElementById('cancel-update-btn');
    const dismissBtn = document.getElementById('dismiss-update-btn');
    
    const isAlreadyUpToDate = message && (
        message.toLowerCase().includes('already up to date') || 
        message.toLowerCase().includes('already up-to-date') || 
        message.toLowerCase().includes('no updates needed')
    );
    
    if (isAlreadyUpToDate) {
        header.textContent = 'SYSTEM UP TO DATE';
        header.style.color = '#00f6ff';
        progressBar.style.width = '100%';
        progressBar.style.backgroundColor = '#00f6ff';
    } else {
        header.textContent = 'UPDATE SUCCEEDED';
        header.style.color = '#00ff00';
        progressBar.style.width = '100%';
        progressBar.style.backgroundColor = '#00ff00';
    }
    
    statusText.textContent = message || 'System successfully updated.';
    cancelBtn.style.display = 'none';
    
    // If it's about to restart/relaunch, don't show the dismiss button to avoid confusion
    if (message && !message.includes('Restarting') && !message.includes('relaunch')) {
        dismissBtn.style.display = 'inline-block';
    } else if (!message) {
        dismissBtn.style.display = 'inline-block';
    }
});

ipcRenderer.on('update-error', (event, error) => {
    const header = document.getElementById('update-header');
    const statusText = document.getElementById('update-status-text');
    const progressBar = document.getElementById('update-progress-bar');
    const cancelBtn = document.getElementById('cancel-update-btn');
    const dismissBtn = document.getElementById('dismiss-update-btn');
    
    header.textContent = 'UPDATE FAILED';
    header.style.color = '#ff3c3c';
    progressBar.style.width = '100%';
    progressBar.style.backgroundColor = '#ff3c3c';
    statusText.textContent = error || 'An error occurred during update.';
    
    cancelBtn.style.display = 'none';
    dismissBtn.style.display = 'inline-block';
});

ipcRenderer.on('hide-update-overlay', () => {
    const overlay = document.getElementById('update-overlay');
    const progressBar = document.getElementById('update-progress-bar');
    overlay.style.display = 'none';
    progressBar.style.width = '0%';
});

// Init
checkSetup();
setInterval(updateStatus, 2000);
updateStatus();
setCoreListen(false); // Start in idle state
