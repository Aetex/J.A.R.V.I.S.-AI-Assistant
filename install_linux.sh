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

jarvis_error_joke() {
    case "$1" in
        python) echo "        JARVIS: I appear to be missing a brain, sir. Python would be a fine place to start." ;;
        system) echo "        Tony Stark: The package manager flinched. Tell it I built this in a cave." ;;
        pip) echo "        Tony Stark: Dependency chaos. Classic. I usually fix this with a suit and questionable confidence." ;;
        ui) echo "        JARVIS: The HUD refuses to assemble. Even Stark tech needs its npm bolts tightened." ;;
        *) echo "        JARVIS: Something broke, sir. I recommend blaming physics until we find the log." ;;
    esac
}

run_with_spinner() {
    message="$1"
    shift
    log_file="$(mktemp)"

    "$@" > "$log_file" 2>&1 &
    pid=$!
    i=0

    while kill -0 "$pid" 2>/dev/null; do
        i=$(( (i + 1) % 4 ))
        case "$i" in
            0) spin='|' ;;
            1) spin='/' ;;
            2) spin='-' ;;
            *) spin='\' ;;
        esac
        printf "\r[*] %s %s" "$message" "$spin"
        sleep 0.12
    done

    wait "$pid"
    status=$?
    printf "\r"

    if [ "$status" -ne 0 ]; then
        saved_log="./jarvis-install-log.log"
        mv "$log_file" "$saved_log"
        echo "[ERROR] $message failed."
        if grep -qiE "Failed to resolve|NameResolutionError|Temporary failure|Could not resolve|unreachable network|Network is unreachable" "$saved_log"; then
            echo "        Network connection failed. Check your internet/DNS, then re-run this installer."
        else
            echo "        Full technical details were saved to $saved_log"
        fi
        return "$status"
    fi

    rm -f "$log_file"
    echo "[OK] $message complete."
    return 0
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
    jarvis_error_joke python
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
    as_root=""
    if [ "$(id -u)" -ne 0 ]; then
        if command_exists sudo; then
            as_root="sudo"
        else
            echo "==================================================="
            echo "  J.A.R.V.I.S. SYSTEM ALERT"
            echo "==================================================="
            echo "[ERROR] This script must install system dependencies, but 'sudo' is not installed."
            echo "        Please run this script as root (e.g., run 'su' first, then run 'sh install_linux.sh')."
            echo "==================================================="
            exit 1
        fi
    fi

    if echo "$distro_ids" | grep -qiE "(^| )(debian|ubuntu|linuxmint|pop)( |$)"; then
        install_cmd="$as_root apt install -y python3-pip python3-venv python3-pyaudio portaudio19-dev nodejs npm"
    elif echo "$distro_ids" | grep -qiE "(^| )(arch|archlinux|manjaro|endeavouros|garuda)( |$)"; then
        install_cmd="$as_root pacman -S --needed --noconfirm python-pyaudio portaudio nodejs npm"
    elif echo "$distro_ids" | grep -qiE "(^| )(fedora|rhel|centos|rocky|almalinux)( |$)"; then
        if command_exists dnf; then
            install_cmd="$as_root dnf install -y python3-pyaudio portaudio-devel nodejs npm"
        else
            install_cmd="$as_root yum install -y python3-pyaudio portaudio-devel nodejs npm"
        fi
    elif echo "$distro_ids" | grep -qiE "(^| )(alpine)( |$)"; then
        install_cmd="$as_root apk add py3-pyaudio portaudio-dev nodejs npm"
    elif echo "$distro_ids" | grep -qiE "(^| )(opensuse|opensuse-tumbleweed|opensuse-leap|suse)( |$)"; then
        install_cmd="$as_root zypper install -y python3-PyAudio portaudio-devel nodejs npm"
    elif echo "$distro_ids" | grep -qiE "(^| )(void)( |$)"; then
        install_cmd="$as_root xbps-install -Sy python3-PyAudio portaudio-devel nodejs npm"
    elif command_exists pacman; then
        install_cmd="$as_root pacman -S --needed --noconfirm python-pyaudio portaudio nodejs npm"
    elif command_exists apt; then
        install_cmd="$as_root apt install -y python3-pip python3-venv python3-pyaudio portaudio19-dev nodejs npm"
    elif command_exists dnf; then
        install_cmd="$as_root dnf install -y python3-pyaudio portaudio-devel nodejs npm"
    elif command_exists yum; then
        install_cmd="$as_root yum install -y python3-pyaudio portaudio-devel nodejs npm"
    elif command_exists apk; then
        install_cmd="$as_root apk add py3-pyaudio portaudio-dev nodejs npm"
    elif command_exists zypper; then
        install_cmd="$as_root zypper install -y python3-PyAudio portaudio-devel nodejs npm"
    elif command_exists xbps-install; then
        install_cmd="$as_root xbps-install -Sy python3-PyAudio portaudio-devel nodejs npm"
    else
        echo "[WARN] Could not detect Linux distribution or supported package manager."
        echo "       Please install python-pyaudio, portaudio, nodejs, and npm using your distro package manager."
        return 0
    fi

    if [ "$(id -u)" -ne 0 ] && command_exists sudo; then
        sudo -v || {
            echo "[ERROR] Administrator authentication failed."
            jarvis_error_joke system
            exit 1
        }
    fi

    if ! run_with_spinner "Installing system dependencies" sh -c "$install_cmd"; then
        echo "[ERROR] System dependency installation failed."
        jarvis_error_joke system
        exit 1
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
. venv/bin/activate
run_with_spinner "Upgrading pip" python3 -m pip install --upgrade pip || {
    echo "[ERROR] Failed to upgrade pip."
    jarvis_error_joke pip
    exit 1
}
run_with_spinner "Installing Python dependencies" pip install --progress-bar off -r requirements.txt || {
    echo "[ERROR] Python dependency installation failed."
    jarvis_error_joke pip
    exit 1
}
echo "[OK] Python dependencies installed."
echo ""

echo "[*] Step 4: Installing UI Components..."
cd ui
run_with_spinner "Installing UI components" npm install --silent || {
    echo "[ERROR] UI dependency installation failed."
    jarvis_error_joke ui
    exit 1
}
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
