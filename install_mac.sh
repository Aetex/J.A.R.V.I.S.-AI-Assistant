#!/bin/bash
echo "==================================================="
echo "  J.A.R.V.I.S. AUTOMATED INSTALLATION (MAC)"
echo "==================================================="
echo ""

cd "$(dirname "$0")"

echo "[*] Step 1: Creating Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[OK] Virtual environment created."
else
    echo "[OK] Virtual environment already exists."
fi
echo ""

echo "[*] Step 2: Installing Python Core Dependencies..."
source venv/bin/activate
python3 -m pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "[OK] Python dependencies installed."
echo ""

echo "[*] Step 3: Installing UI Components..."
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
