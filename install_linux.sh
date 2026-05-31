#!/bin/bash
echo "==================================================="
echo "  J.A.R.V.I.S. AUTOMATED INSTALLATION (LINUX)"
echo "==================================================="
echo ""

cd "$(dirname "$0")"

run_as_root() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    else
        sudo "$@"
    fi
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_python() {
    echo "[*] Pre-flight: Checking Python..."

    if command_exists python3; then
        echo "[OK] Python detected: $(python3 --version 2>&1)"
        return 0
    fi

    python_install_command="Install Python 3 using your distro package manager."

    if [ -r /etc/os-release ]; then
        . /etc/os-release
        distro_ids=" ${ID:-} ${ID_LIKE:-} "

        if echo "$distro_ids" | grep -qiE "(^| )(debian|ubuntu|linuxmint|pop)( |$)"; then
            python_install_command="sudo apt install -y python3 python3-venv python3-pip"
        elif echo "$distro_ids" | grep -qiE "(^| )(arch|archlinux|manjaro|endeavouros|garuda)( |$)"; then
            python_install_command="sudo pacman -S --needed python python-pip"
        elif echo "$distro_ids" | grep -qiE "(^| )(fedora|rhel|centos|rocky|almalinux)( |$)"; then
            if command_exists dnf; then
                python_install_command="sudo dnf install -y python3 python3-pip"
            else
                python_install_command="sudo yum install -y python3 python3-pip"
            fi
        elif echo "$distro_ids" | grep -qiE "(^| )(alpine)( |$)"; then
            python_install_command="sudo apk add python3 py3-pip"
        elif echo "$distro_ids" | grep -qiE "(^| )(opensuse|opensuse-tumbleweed|opensuse-leap|suse)( |$)"; then
            python_install_command="sudo zypper install -y python3 python3-pip"
        elif echo "$distro_ids" | grep -qiE "(^| )(void)( |$)"; then
            python_install_command="sudo xbps-install -Sy python3 python3-pip"
        fi
    fi

    if [ "$python_install_command" = "Install Python 3 using your distro package manager." ]; then
        if command_exists pacman; then
            python_install_command="sudo pacman -S --needed python python-pip"
        elif command_exists apt; then
            python_install_command="sudo apt install -y python3 python3-venv python3-pip"
        elif command_exists dnf; then
            python_install_command="sudo dnf install -y python3 python3-pip"
        elif command_exists yum; then
            python_install_command="sudo yum install -y python3 python3-pip"
        elif command_exists apk; then
            python_install_command="sudo apk add python3 py3-pip"
        elif command_exists zypper; then
            python_install_command="sudo zypper install -y python3 python3-pip"
        elif command_exists xbps-install; then
            python_install_command="sudo xbps-install -Sy python3 python3-pip"
        fi
    fi

    echo "==================================================="
    echo "  J.A.R.V.I.S. SYSTEM ALERT"
    echo "==================================================="
    echo "[ERROR] Python 3 is not installed or not available on PATH."
    echo "        Arc reactor offline. Please install Python 3 with:"
    echo "        $python_install_command"
    echo "        Then re-run this script."
    echo "==================================================="
    exit 1
}

install_system_dependencies() {
    echo "[*] Step 1: Installing system dependencies..."

    if [ -r /etc/os-release ]; then
        . /etc/os-release
    else
        ID=""
        ID_LIKE=""
        PRETTY_NAME="unknown"
    fi

    distro_ids=" ${ID:-} ${ID_LIKE:-} "

    if echo "$distro_ids" | grep -qiE "(^| )(debian|ubuntu|linuxmint|pop)( |$)"; then
        run_as_root apt install -y python3-pyaudio portaudio19-dev nodejs npm
    elif echo "$distro_ids" | grep -qiE "(^| )(arch|archlinux|manjaro|endeavouros|garuda)( |$)"; then
        run_as_root pacman -S --needed --noconfirm python-pyaudio portaudio nodejs npm
    elif echo "$distro_ids" | grep -qiE "(^| )(fedora|rhel|centos|rocky|almalinux)( |$)"; then
        if command_exists dnf; then
            run_as_root dnf install -y python3-pyaudio portaudio-devel nodejs npm
        else
            run_as_root yum install -y python3-pyaudio portaudio-devel nodejs npm
        fi
    elif echo "$distro_ids" | grep -qiE "(^| )(alpine)( |$)"; then
        run_as_root apk add py3-pyaudio portaudio-dev nodejs npm
    elif echo "$distro_ids" | grep -qiE "(^| )(opensuse|opensuse-tumbleweed|opensuse-leap|suse)( |$)"; then
        run_as_root zypper install -y python3-PyAudio portaudio-devel nodejs npm
    elif echo "$distro_ids" | grep -qiE "(^| )(void)( |$)"; then
        run_as_root xbps-install -Sy python3-PyAudio portaudio-devel nodejs npm
    elif command_exists pacman; then
        run_as_root pacman -S --needed --noconfirm python-pyaudio portaudio nodejs npm
    elif command_exists apt; then
        run_as_root apt install -y python3-pyaudio portaudio19-dev nodejs npm
    elif command_exists dnf; then
        run_as_root dnf install -y python3-pyaudio portaudio-devel nodejs npm
    elif command_exists yum; then
        run_as_root yum install -y python3-pyaudio portaudio-devel nodejs npm
    elif command_exists apk; then
        run_as_root apk add py3-pyaudio portaudio-dev nodejs npm
    elif command_exists zypper; then
        run_as_root zypper install -y python3-PyAudio portaudio-devel nodejs npm
    elif command_exists xbps-install; then
        run_as_root xbps-install -Sy python3-PyAudio portaudio-devel nodejs npm
    else
        echo "[WARN] Could not detect Linux distribution or supported package manager."
        echo "       Please install python-pyaudio, portaudio, nodejs, and npm using your distro package manager."
        return 0
    fi

    echo "[OK] System dependencies installed."
}

check_python
echo ""

install_system_dependencies
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
