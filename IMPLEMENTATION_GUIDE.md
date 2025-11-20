# MCP23S17 Implementation Guide

## Complete Setup & Deployment

This guide walks through everything needed to get the MCP23S17 matrix controller running on a Raspberry Pi 5.

## Phase 1: Preparation

### 1.1 Prerequisites
- Raspberry Pi 5 (4 GB RAM minimum)
- Raspberry Pi OS (Bookworm or newer)
- Python 3.9+
- SPI-capable hardware (MCP23S17 chip)

### 1.2 System Update
```bash
sudo apt update
sudo apt upgrade -y
```

### 1.3 Python Setup
```bash
# Verify Python version
python3 --version

# Install pip if needed
sudo apt install python3-pip -y

# Install virtual environment
sudo apt install python3-venv -y
```

## Phase 2: Repository Setup

### 2.1 Clone or Download Project
```bash
cd ~
git clone <repo-url> mcp23s17_matrix_controller
# or download and extract zip
cd mcp23s17_matrix_controller
```

### 2.2 Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Phase 3: Hardware Setup

### 3.1 Enable SPI Interface
```bash
sudo raspi-config
# Interfacing Options → SPI → Enable → Yes
```

### 3.2 Verify SPI
```bash
# Check SPI is available
ls -la /dev/spidev*
# Should show: /dev/spidev0.0 /dev/spidev0.1

# Or check with raspi-gpio
sudo raspi-gpio get
```

### 3.3 Wiring Reference
See `HARDWARE_WIRING.md` for:
- Complete pin connections
- MCP23S17 pinout
- BJT transistor circuit
- Decoupling capacitor placement
- Multiple chip configuration

### 3.4 Physical Wiring
```
Raspberry Pi → MCP23S17
GPIO 11 (SCK)  → Pin 19 (SCK)
GPIO 10 (MOSI) → Pin 21 (SI)
GPIO 9 (MISO)  → Pin 20 (SO)
GPIO 8 (CE0)   → Pin 22 (CS)
3.3V           → Pin 18 (VCC) + 0.1µF cap
GND            → Pin 9 (GND)
3.3V           → Pin 23 (RESET)
```

### 3.5 Verify Connections
```bash
# Check with multimeter (powered off)
# Test for shorts between adjacent pins
# Verify all connections are secure

# Check resistance with multimeter
# VCC to GND should show resistance (not 0Ω)
```

## Phase 4: Testing

### 4.1 SPI Hardware Test
```bash
# Test SPI communication
python3 -c "import spidev; spi=spidev.SpiDev(); spi.open(0,0); print('SPI OK'); spi.close()"
```

### 4.2 Basic Library Test
```python
from mcp23s17_controller import MCP23S17

try:
    mcp = MCP23S17(bus=0, device=0)
    print("MCP23S17 initialized successfully")
    
    # Test port state
    state_a = mcp.get_port_state('A')
    state_b = mcp.get_port_state('B')
    print(f"Port A: 0x{state_a:02X}")
    print(f"Port B: 0x{state_b:02X}")
    
    # Test pin high
    mcp.set_pin_high('A', 0)
    print("Pin A0 set HIGH")
    
    # Test pin low
    mcp.set_pin_low('A', 0)
    print("Pin A0 set LOW")
    
    print("✓ All tests passed!")
    mcp.cleanup()
except Exception as e:
    print(f"✗ Test failed: {e}")
```

### 4.3 Run Example Suite
```bash
# Test all functionality
python examples.py
```

## Phase 5: Integration

### 5.1 Create Your Script
```python
from mcp23s17_controller import MatrixController
import time

# Initialize
controller = MatrixController(num_rows=4, num_cols=4)

try:
    # Your matrix operations here
    controller.press_button(row=0, col=0, duration=0.1)
    
except KeyboardInterrupt:
    print("Interrupted")
except Exception as e:
    print(f"Error: {e}")
finally:
    controller.cleanup()
```

### 5.2 Test Your Script
```bash
python your_script.py
```

## Phase 6: Production Deployment

### 6.1 Create Systemd Service (Optional)

Create `/etc/systemd/system/mcp23s17.service`:
```ini
[Unit]
Description=MCP23S17 Matrix Controller
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=10
User=pi
WorkingDirectory=/home/pi/mcp23s17_matrix_controller
Environment="PATH=/home/pi/mcp23s17_matrix_controller/venv/bin"
ExecStart=/home/pi/mcp23s17_matrix_controller/venv/bin/python3 your_script.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 6.2 Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp23s17
sudo systemctl start mcp23s17
```

### 6.3 Monitor Service
```bash
# Check status
sudo systemctl status mcp23s17

# View logs
sudo journalctl -u mcp23s17 -f

# Stop service
sudo systemctl stop mcp23s17
```

### 6.4 Cron Job (Alternative)

```bash
crontab -e
# Add line:
# @reboot cd /home/pi/mcp23s17_matrix_controller && source venv/bin/activate && python3 your_script.py >> /home/pi/matrix.log 2>&1
```

## Phase 7: Monitoring & Maintenance

### 7.1 Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 7.2 Log Output
```bash
# Redirect output to file
python your_script.py >> matrix.log 2>&1

# Monitor live
tail -f matrix.log
```

### 7.3 Performance Monitoring
```bash
# Monitor CPU/Memory
top

# Monitor SPI bus
# Use oscilloscope or logic analyzer on SPI pins
```

## Phase 8: Troubleshooting

### Issue: Import Error
```
ImportError: No module named 'spidev'
```
**Solution:**
```bash
source venv/bin/activate
pip install spidev
```

### Issue: SPI Device Not Found
```
OSError: [Errno 2] No such file or directory: '/dev/spidev0.0'
```
**Solution:**
```bash
# Enable SPI
sudo raspi-config
# Check again
ls /dev/spidev*
```

### Issue: Permission Denied
```
PermissionError: [Errno 13] Permission denied: '/dev/spidev0.0'
```
**Solution:**
```bash
# Add user to spi group
sudo usermod -aG spi $USER
# Log out and back in
```

### Issue: No Response from MCP23S17
**Checklist:**
1. SPI enabled: `sudo raspi-config`
2. Wiring correct: Check against `HARDWARE_WIRING.md`
3. VCC and GND connected: Use multimeter
4. Decoupling capacitor installed: 0.1µF on VCC
5. RESET pulled high: Check continuity to VCC
6. SPI speed not too high: Try 100kHz

## Advanced Configuration

### 7.1 Multiple MCP23S17 Chips
```python
# Use different chip select pins
mcp1 = MCP23S17(device=0, chip_select=0)
mcp2 = MCP23S17(device=0, chip_select=1)
```

### 7.2 Custom SPI Speed
```python
# Use faster speed if needed
mcp = MCP23S17(speed_hz=400000)
```

### 7.3 Modify Matrix Size
```python
# For 8x8 matrix
controller = MatrixController(num_rows=8, num_cols=8)
```

## Optimization Tips

### 1. Power Management
```bash
# Check power state
vcgencmd get_throttled

# Monitor voltage
vcgencmd measure_volts
```

### 2. SPI Performance
```python
# Test different speeds
for speed in [100000, 200000, 400000, 1000000]:
    mcp = MCP23S17(speed_hz=speed)
    # Test reliability
```

### 3. Timing Optimization
```python
# Find minimum pulse duration
for duration in [0.05, 0.075, 0.1, 0.15]:
    mcp.pulse_pin('A', 0, duration=duration)
```

## Backup & Recovery

### Create Backup
```bash
# Backup project
tar -czf mcp23s17_backup.tar.gz mcp23s17_matrix_controller/

# Backup system
sudo dd if=/dev/mmcblk0 of=/mnt/usb/rpi_backup.img
```

### Restore from Backup
```bash
# Restore project
tar -xzf mcp23s17_backup.tar.gz

# Restore system (from another machine)
sudo dd if=/mnt/usb/rpi_backup.img of=/dev/mmcblk0
```

## Documentation Reference

| Document | Purpose |
|----------|---------|
| `README.md` | Full API documentation |
| `QUICK_REFERENCE.md` | Quick command lookup |
| `HARDWARE_WIRING.md` | Detailed wiring guide |
| `PROJECT_SUMMARY.md` | Project overview |
| `IMPLEMENTATION_GUIDE.md` | This file |

## Useful Commands

### Project Management
```bash
# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Update packages
pip install --upgrade -r requirements.txt
```

### Raspberry Pi Commands
```bash
# Check SPI status
gpio readall | grep SPI

# Check GPIO pins in use
gpioinfo

# Monitor real-time activity
watch -n 1 'cat /proc/interrupts | head -20'
```

### Testing Commands
```bash
# Test Python import
python3 -c "from mcp23s17_controller import MCP23S17; print('OK')"

# Test SPI
python3 -c "import spidev; print('SPI OK')"

# Run all examples
python examples.py
```

## Checklist: First-Time Setup

- [ ] Raspberry Pi OS installed and updated
- [ ] Python 3.9+ installed
- [ ] Project cloned/extracted
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] SPI enabled in `raspi-config`
- [ ] SPI devices visible (`ls /dev/spidev*`)
- [ ] Hardware wired according to guide
- [ ] Wiring double-checked with multimeter
- [ ] Basic test successful
- [ ] Example suite runs without errors
- [ ] Custom script tested
- [ ] Service configured (optional)
- [ ] Logging enabled for debugging

## Next Steps

1. **Test with provided examples**: `python examples.py`
2. **Adapt for your matrix size**: Modify `MatrixController` parameters
3. **Create custom sequences**: Use `press_sequence()` with your data
4. **Deploy to production**: Setup systemd service
5. **Monitor performance**: Enable logging and track metrics

## Support Resources

- **MCP23S17 Datasheet**: https://ww1.microchip.com/en-US/product/mcp23s17
- **RPi 5 Documentation**: https://www.raspberrypi.com/documentation/
- **Python SPI**: https://github.com/doceme/py-spidev
- **GPIO Pinout**: `gpio readall`

## Quick Start Summary

```bash
# 1. Clone project
cd ~ && git clone <repo> mcp23s17_matrix_controller && cd mcp23s17_matrix_controller

# 2. Setup Python
python3 -m venv venv && source venv/bin/activate

# 3. Install packages
pip install -r requirements.txt

# 4. Enable SPI
sudo raspi-config  # Interfacing Options → SPI

# 5. Test
python examples.py

# 6. Use in your code
from mcp23s17_controller import MatrixController
controller = MatrixController()
controller.press_button(0, 0)
controller.cleanup()
```

---

**Setup Complete!** 🎉

Your MCP23S17 matrix controller is ready to use. Refer to the Quick Reference for common operations and README for full API documentation.
