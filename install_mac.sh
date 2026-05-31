#!/bin/bash
echo "==================================================="
echo "  J.A.R.V.I.S. AUTOMATED INSTALLATION (MAC)"
echo "==================================================="
echo ""

cd "$(dirname "$0")"

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

install_node_dependencies() {
    echo "[*] Step 1: Checking Node.js and npm..."

    if command_exists node && command_exists npm; then
        echo "[OK] Node.js and npm are already installed."
        return 0
    fi

    if ! command_exists brew; then
        echo "[*] Homebrew is required to install Node.js/npm. Installing Homebrew..."
        NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        if [ -x "/opt/homebrew/bin/brew" ]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [ -x "/usr/local/bin/brew" ]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi

    if ! command_exists brew; then
        echo "[ERROR] Homebrew installation was not found on PATH."
        echo "        Install Node.js from https://nodejs.org/ and re-run this script."
        exit 1
    fi

    brew install node
    echo "[OK] Node.js and npm installed."
}

install_node_dependencies
echo ""

echo "[*] Step 2: Creating Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[OK] Virtual environment created."
else
    echo "[OK] Virtual environment already exists."
fi
echo ""

echo "[*] Step 3: Installing Python Core Dependencies..."
source venv/bin/activate
python3 -m pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "[OK] Python dependencies installed."
echo ""

echo "[*] Step 4: Installing UI Components..."
cd ui
npm install
cd ..
echo "[OK] UI components installed."
echo ""

echo "==================================================="
echo "  INSTALLATION COMPLETE!"
echo "==================================================="
echo ""
echo "Please complete the final step manually:"
echo "1. Rename .env.example to .env"
echo "2. Open it and paste your API key inside."
echo ""
echo "Once done, you can launch the system using:"
echo "./launch_jarvis.sh"
echo ""
