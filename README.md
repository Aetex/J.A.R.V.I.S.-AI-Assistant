# J.A.R.V.I.S. | The Holographic AI Assistant By AeteX

> [!IMPORTANT]
> **Original project by AeteX.** Forks and modifications are welcome. Please keep original credit when sharing or modifying this project.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Electron](https://img.shields.io/badge/platform-Electron-blueviolet.svg)](https://www.electronjs.org/)

**Current version:** v0.3.5

> **Development warning:** JARVIS v0.3.5 is still under active development. Expect some rough edges and possible bugs while the systems are being upgraded.

> *"I am Iron Man."*

A sophisticated, holographic AI assistant inspired by Iron Man's J.A.R.V.I.S. This project combines a high-performance Python backend (powered by Groq or Google Gemini) with a stunning Electron-based glassmorphism HUD.

---

## 1. Get Your Free API Key

> *"Give me a few hours. I'll have something better figured out." — Tony Stark*

This project supports cloud and local AI engines. You can use Groq, Gemini, or LM Studio.

### Option A: Groq API
1. Visit the [Groq Cloud Console](https://console.groq.com/keys).
2. Create an API Key. This provides lightning-fast responses using Groq's high-speed inference.

### Option B: Google Gemini API
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create a free API Key. This provides a massive context window and is optimized for the free tier.

### Option C: LM Studio (Local / Highly Experimental — Not Recommended)

> **Warning:** This option is highly experimental, not recommended for daily use, and is turned off (`false`) by default.

1. Install and open [LM Studio](https://lmstudio.ai/).
2. Download and load a chat/instruct model.
3. Start LM Studio's local server.
4. In `.env`, set:
   ```env
   LM_STUDIO_ENABLED=true
   LM_STUDIO_URL="http://127.0.0.1:1234/v1/chat/completions"
   LM_STUDIO_MODEL="local-model"
   ```

*Note: If `LM_STUDIO_ENABLED=true`, JARVIS will use LM Studio first. Otherwise, Gemini is prioritized over Groq when both cloud keys are provided.*

---

## 2. Installation & Setup

> *"Sometimes you gotta run before you can walk." — Tony Stark*

We offer two installation paths depending on your technical comfort level.

### Path A: Regular Users (Installer / Portable)

> **Under Maintenance** — The pre-built `.exe` installer and `.zip` portable are currently being fixed and will be available again in a future update. In the meantime, please use the script installation below — it is easier than it sounds and takes less than 5 minutes!

---

### Path B: Power Users / Developers

> *"Let's face it, this is not the worst thing you've caught me doing." — Tony Stark*

If you want to edit the code, tweak the UI, or run the system natively across Windows, macOS, or Linux, follow the source-code installation below:

<details>
<summary><b>Windows Setup (Click to expand)</b></summary>

1. **Option A: Clone with Git** (Recommended):
   ```powershell
   git clone https://github.com/TheUnkownDev/J.A.R.V.I.S.-AI-Assistant.git
   cd J.A.R.V.I.S.-AI-Assistant
   ```
   **Option B: Download ZIP**:
   - Click the green **"Code"** button at the top of this page.
   - Select **"Download ZIP"**.
   - Extract the folder and open it.
2. **Run the Installer**:
   - Double-click the `install_windows.bat` file.
   - Wait for it to say "INSTALLATION COMPLETE!"
3. **Run & Configure**:
   - Double-click `launch_jarvis.bat`.
   - Once the HUD opens, configure your API keys (Groq or Gemini) directly from the settings menu.
</details>

<details>
<summary><b>macOS Setup (Click to expand)</b></summary>

1. **Option A: Clone with Git** (Recommended):
   ```bash
   git clone https://github.com/TheUnkownDev/J.A.R.V.I.S.-AI-Assistant.git
   cd J.A.R.V.I.S.-AI-Assistant
   ```
   **Option B: Download ZIP**:
   - Click the green **"Code"** button at the top of this page.
   - Select **"Download ZIP"**.
   - Extract the folder and open it in your terminal.
2. **Run the Installer**:
   ```bash
   sh install_mac.sh
   ```
3. **Run & Configure**:
   ```bash
   sh launch_jarvis.sh
   ```
   - Once the HUD opens, configure your API keys (Groq or Gemini) directly from the settings menu.
</details>

<details>
<summary><b>Linux Setup (Click to expand)</b></summary>

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/TheUnkownDev/J.A.R.V.I.S.-AI-Assistant.git
   cd J.A.R.V.I.S.-AI-Assistant
   ```
2. **Run the Installer**:
   ```bash
   sh install_linux.sh
   ```
3. **Run & Configure**:
   ```bash
   sh launch_jarvis.sh
   ```
   - Once the HUD opens, configure your API keys (Groq or Gemini) directly from the settings menu.
</details>

---

## 3. How to Use

> *"JARVIS, it's time for a little upgrades." — Tony Stark*

- **Activation**: Say "Jarvis" followed by your command.
- **Modes**: Use the **[MINI]** button for a compact hologram or **[EXIT]** to shut down.
- **Debugging**: Say "Jarvis, enter debugging mode" to see live system logs.
- **Interruption**: Click the central JARVIS core at any time to silence him or stop a long response.

---

## 4. Troubleshooting

> *"I'm going to need a little time to work on that." — Tony Stark*

- **Microphone not detected**: Ensure your default input device is set correctly in OS settings.
- **Backend Error**: Verify that you have configured your API keys inside the HUD's settings panel.
- **UI not loading**: Ensure you ran `npm install` inside the `ui` folder.

---

*Inspired by the MCU. Developed for the future.*
