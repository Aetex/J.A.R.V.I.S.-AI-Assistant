const { ipcRenderer } = require('electron');

const input = document.getElementById('user-input');
const chatLog = document.getElementById('chat-log');
const micBtn = document.getElementById('mic-btn');
const core = document.getElementById('jarvis-core');
const statusText = document.getElementById('status-text');

const cpuBar = document.getElementById('cpu-bar');
const memBar = document.getElementById('mem-bar');
const volBar = document.getElementById('vol-bar');
const cpuVal = document.getElementById('cpu-val');
const memVal = document.getElementById('mem-val');
const volVal = document.getElementById('vol-val');

const BACKEND_URL = 'http://127.0.0.1:8000';

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `msg msg-${sender}`;
    div.innerText = sender === 'jarvis' ? `> ${text}` : `[USER]: ${text}`;
    chatLog.appendChild(div);
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
    
    core.classList.add('thinking');
    statusText.innerText = "ANALYZING...";
    
    try {
        const res = await fetch(`${BACKEND_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });

        core.classList.remove('thinking');
        statusText.innerText = "SYSTEM IDLE";

        if (!res.ok) {
            const errorData = await res.json();
            addMessage(`Sir, my processors are reporting an error: ${errorData.detail || 'Internal Error'}`, 'jarvis');
            return;
        }

        const data = await res.json();
        handleJarvisResponse(data);
        
    } catch (error) {
        core.classList.remove('thinking');
        statusText.innerText = "SYSTEM IDLE";
        addMessage("I'm having trouble connecting to my core processors, sir. Please ensure the backend is running.", 'jarvis');
        console.error(error);
    }
}

async function updateStatus() {
    try {
        const res = await fetch(`${BACKEND_URL}/status`);
        const data = await res.json();
        
        cpuBar.style.width = `${data.cpu}%`;
        cpuVal.innerText = `${Math.round(data.cpu)}%`;
        
        memBar.style.width = `${data.memory}%`;
        memVal.innerText = `${Math.round(data.memory)}%`;
        
        volBar.style.width = `${data.volume}%`;
        volVal.innerText = `${data.volume}%`;
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
});

micBtn.addEventListener('click', async () => {
    micBtn.style.color = "red";
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
        micBtn.innerText = "🎙️";
    }
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
    try {
        // 1. Tell backend to shut down
        fetch(`${BACKEND_URL}/shutdown`, { method: 'POST' });
        // 2. Close UI immediately
        ipcRenderer.send('quit-app');
    } catch (e) {
        ipcRenderer.send('quit-app'); // Force close UI anyway
    }
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
    // Visual feedback: Make the core pulse faster or change color
    core.style.boxShadow = "0 0 50px #ff0000"; 
    setTimeout(() => { core.style.boxShadow = ""; }, 2000);
});

eventSource.addEventListener('user_speech', (e) => {
    const data = JSON.parse(e.data);
    addMessage(data.text, 'user');
    // Trigger thinking state for voice commands
    core.classList.add('thinking');
    statusText.innerText = "ANALYZING...";
});

eventSource.addEventListener('jarvis_response', (e) => {
    const data = JSON.parse(e.data);
    // Hide thinking state when response arrives
    core.classList.remove('thinking');
    statusText.innerText = "SYSTEM IDLE";
    handleJarvisResponse(data);
});

// Click-through handling
window.addEventListener('mousemove', (event) => {
    if (event.target === document.documentElement || event.target === document.body) {
        ipcRenderer.send('set-ignore-mouse-events', true, { forward: true });
    } else {
        ipcRenderer.send('set-ignore-mouse-events', false);
    }
});

// Init
setInterval(updateStatus, 2000);
updateStatus();
