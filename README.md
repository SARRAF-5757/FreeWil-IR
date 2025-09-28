# FreeWili-IR Games & Simulations

This repository contains three Python scripts that demonstrate different capabilities of FreeWili devices:

## Scripts Overview

### 🎮 `game.py` - Two-Mode IR Communication Game
A two-player interactive game using FreeWili devices and IR communication. Players can switch between SEND and RECEIVE modes using the red button, and send/receive colored light signals through IR communication.

**Features:**
- Mode switching between SEND and RECEIVE using the red button
- Color-coded IR signal transmission and reception
- LED feedback for current mode and received signals
- Real-time button state monitoring

### 🎯 `game_turn-based.py` - Turn-Based IR Game
A turn-based multiplayer game where players must respond to IR signals within a time limit. The game features a countdown timer and requires quick responses to prevent game over.

**Features:**
- Turn-based gameplay with time pressure
- 10-second countdown timer before game over
- Random light generation for each turn
- IR signal matching mechanics

### 🌟 `accel-sim.py` - Accelerometer Light Trail Simulation
An interactive light trail simulation that responds to device tilt using the built-in accelerometer. Creates a smooth, animated light trail that follows the device's orientation.

**Features:**
- Real-time accelerometer data processing
- Smooth light trail animation with decay effects
- Tilt-based LED position mapping
- Low-pass filtering for stable movement
- Efficient LED update system

## Installation & Setup Tutorial

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- FreeWili device(s) connected via USB

### Step 1: Install Python and pip

**On macOS (using Homebrew):**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python (includes pip)
brew install python
```

**On Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. pip will be installed automatically

**On Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 2: Install FreeWili Library

```bash
# Install the freewili library
pip install freewili

# Or if you have multiple Python versions, use:
pip3 install freewili
```

### Step 3: Connect Your FreeWili Device

1. Connect your FreeWili device to your computer via USB
2. Ensure the device is properly powered on
3. The device should be automatically detected by the system

### Step 4: Verify Installation

```bash
# Test if freewili is properly installed
python -c "import freewili; print('FreeWili library installed successfully!')"
```

### Step 5: Run the Scripts

**For the two-mode IR game:**
```bash
python game.py
```

**For the turn-based game:**
```bash
python game_turn-based.py
```

**For the accelerometer simulation:**
```bash
python accel-sim.py
```

## Usage Instructions

### Two-Mode IR Game (`game.py`)
1. Run the script with two FreeWili devices
2. Use the red button to switch between SEND and RECEIVE modes
3. In SEND mode: Press any colored button to send that color's signal
4. In RECEIVE mode: Wait for the other device's signal and respond accordingly

### Turn-Based Game (`game_turn-based.py`)
1. Run the script on both devices
2. Press any button to send your color signal
3. Respond to incoming signals within 10 seconds
4. Game ends if you don't respond in time

### Accelerometer Simulation (`accel-sim.py`)
1. Run the script with a single FreeWili device
2. Tilt the device left or right to move the light trail
3. The trail will follow your device's orientation smoothly
4. Press Ctrl+C to exit

## Troubleshooting

**Device not found:**
- Ensure the FreeWili device is properly connected via USB
- Check that the device is powered on
- Try running the script with administrator/sudo privileges

**Import errors:**
- Verify freewili is installed: `pip list | grep freewili`
- Try reinstalling: `pip uninstall freewili && pip install freewili`

**Permission errors:**
- On Linux/macOS, you may need to add your user to the dialout group:
  ```bash
  sudo usermod -a -G dialout $USER
  ```
- Log out and log back in for changes to take effect

## Requirements

- Python 3.7+
- freewili library
- FreeWili device(s)
- USB connection

## License

This project is open source. Please check the FreeWili library license for usage terms.
