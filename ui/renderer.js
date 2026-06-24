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

// Menu System
const menuToggle = document.getElementById('menu-toggle');
const menuDropdown = document.getElementById('menu-dropdown');
let isMenuOpen = false;

menuToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    isMenuOpen = !isMenuOpen;
    menuDropdown.classList.toggle('active', isMenuOpen);
    menuToggle.classList.toggle('active', isMenuOpen);
    
    // Add slight bounce animation
    menuToggle.style.animation = 'none';
    setTimeout(() => {
        menuToggle.style.animation = '';
    }, 10);
});

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.header-menu-container')) {
        isMenuOpen = false;
        menuDropdown.classList.remove('active');
        menuToggle.classList.remove('active');
    }
});

// Close menu when selecting an item
const menuItems = document.querySelectorAll('.menu-item');
menuItems.forEach(item => {
    item.addEventListener('click', () => {
        // Smooth close animation
        menuDropdown.style.transition = 'all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)';
        setTimeout(() => {
            menuDropdown.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
        }, 200);
    });
});

// View Toggling
const miniToggle = document.getElementById('mini-toggle');
const exitBtn = document.getElementById('exit-btn');
const fullView = document.getElementById('full-view');
const miniView = document.getElementById('mini-view');
const miniCore = document.getElementById('mini-core');
let isMini = false;

exitBtn.addEventListener('click', async () => {
    // Close menu first
    isMenuOpen = false;
    menuDropdown.classList.remove('active');
    menuToggle.classList.remove('active');
    
    addMessage("Shutting down all systems, sir.", 'jarvis');
    
    // Shutdown animation
    const container = document.getElementById('full-view');
    if (container) {
        container.style.transition = 'all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        container.style.opacity = '0';
        container.style.transform = 'scale(0.95) rotateX(10deg)';
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

function toggleView() {
    // Close menu first
    isMenuOpen = false;
    menuDropdown.classList.remove('active');
    menuToggle.classList.remove('active');
    
    isMini = !isMini;
    document.body.classList.toggle('mini-mode');
    if (isMini) {
        fullView.style.transition = 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
        fullView.style.opacity = '0';
        setTimeout(() => {
            fullView.style.display = 'none';
            miniView.style.display = 'flex';
            miniView.style.animation = 'slideInRight 0.6s ease-out';
            ipcRenderer.send('resize-window', 150, 150);
        }, 400);
    } else {
        miniView.style.animation = 'slideInLeft 0.4s ease-out';
        miniView.style.opacity = '0';
        setTimeout(() => {
            fullView.style.display = 'grid';
            fullView.style.opacity = '0';
            fullView.style.transform = 'scale(0.95)';
            miniView.style.display = 'none';
            fullView.style.transition = 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
            requestAnimationFrame(() => {
                fullView.style.opacity = '1';
                fullView.style.transform = 'scale(1)';
            });
            ipcRenderer.send('resize-window', 1200, 800);
        }, 400);
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

document.getElementById('keys-btn').addEventListener('click', openSetupOverlay);

// Init
checkSetup();
setInterval(updateStatus, 2000);
updateStatus();
setCoreListen(false); // Start in idle state
