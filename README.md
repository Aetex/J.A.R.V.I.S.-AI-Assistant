# 💠 J.A.R.V.I.S. | The Holographic AI Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Electron](https://img.shields.io/badge/platform-Electron-blueviolet.svg)](https://www.electronjs.org/)

A sophisticated, holographic AI assistant inspired by Iron Man's J.A.R.V.I.S. This project combines a high-performance Python backend (powered by Groq or Google Gemini) with a stunning Electron-based glassmorphism HUD.

---

## 🔑 1. Get Your Free API Key
This project supports two high-performance AI engines. You can use either (or both!):

### Option A: Groq API
1. Visit the [Groq Cloud Console](https://console.groq.com/keys).
2. Create an API Key. This provides lightning-fast responses using Groq's high-speed inference.

### Option B: Google Gemini API
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create a free API Key. This provides a massive context window and is optimized for the free tier.

*Note: If both keys are provided, JARVIS will prioritize Gemini.*

---

## 🚀 2. Installation & Setup

Choose your operating system below for specific instructions:

<details>
<summary><b>🪟 Windows Setup (Click to expand)</b></summary>

1. **Option A: Clone with Git** (Recommended):
   ```powershell
   git clone https://github.com/TheUnkownDev/J.A.R.V.I.S.-AI-Assistant.git
   cd J.A.R.V.I.S.-AI-Assistant
   ```
   **Option B: Download ZIP**:
   - Click the green **"Code"** button at the top of this page.
   - Select **"Download ZIP"**.
   - Extract the folder and open it in your terminal.
2. **Environment Setup**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure API**:
   - Rename `.env.example` to `.env`.
   - Open `.env` and paste your key(s):
     - `GROQ_API_KEY="your_key_here"`
     - `GOOGLE_API_KEY="your_key_here"`
4. **UI Setup**:
   ```powershell
   cd ui
   npm install
   cd ..
   ```
5. **Run**:
   - Double-click `launch_jarvis.bat`.
</details>

<details>
<summary><b>🍎 macOS Setup (Click to expand)</b></summary>

1. **Option A: Clone with Git** (Recommended):
   ```bash
   git clone https://github.com/TheUnkownDev/J.A.R.V.I.S.-AI-Assistant.git
   cd J.A.R.V.I.S.-AI-Assistant
   ```
   **Option B: Download ZIP**:
   - Click the green **"Code"** button at the top of this page.
   - Select **"Download ZIP"**.
   - Extract the folder and open it in your terminal.
2. **Environment Setup**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configure API**:
   - Rename `.env.example` to `.env`.
   - Open `.env` and paste your key(s):
     - `GROQ_API_KEY="your_key_here"`
     - `GOOGLE_API_KEY="your_key_here"`
4. **UI Setup**:
   ```bash
   cd ui
   npm install
   cd ..
   ```
5. **Run**:
   ```bash
   sh launch_jarvis.sh
   ```
</details>

<details>
<summary><b>🐧 Linux Setup (Click to expand)</b></summary>

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/TheUnkownDev/J.A.R.V.I.S.-AI-Assistant.git
   cd J.A.R.V.I.S.-AI-Assistant
   ```
2. **Dependencies**:
   Ensure you have `pyaudio` dependencies: `sudo apt-get install python3-pyaudio portaudio19-dev`
3. **Environment Setup**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Configure API**:
   - Rename `.env.example` to `.env`.
   - Open `.env` and paste your key(s):
     - `GROQ_API_KEY="your_key_here"`
     - `GOOGLE_API_KEY="your_key_here"`
5. **UI Setup**:
   ```bash
   cd ui
   npm install
   cd ..
   ```
6. **Run**:
   ```bash
   sh launch_jarvis.sh
   ```
</details>

---

## 💠 3. How to Use
- **Activation**: Say "Jarvis" followed by your command.
- **Modes**: Use the **[MINI]** button for a compact hologram or **[EXIT]** to shut down.
- **Debugging**: Say "Jarvis, enter debugging mode" to see live system logs.
- **Interruption**: Click the central JARVIS core at any time to silence him or stop a long response.

---

## 🛠️ Troubleshooting
- **Microphone not detected**: Ensure your default input device is set correctly in OS settings.
- **Backend Error**: Verify your `.env` file contains the correct `GROQ_API_KEY`.
- **UI not loading**: Ensure you ran `npm install` inside the `ui` folder.

---
*Inspired by the MCU. Developed for the future.*
