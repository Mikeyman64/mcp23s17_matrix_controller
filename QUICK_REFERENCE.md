# MCP23S17 Quick Reference

## Project Structure
```
mcp23s17_matrix_controller/
├── mcp23s17_controller.py      # Main library
├── examples.py                  # Usage examples
├── requirements.txt            # Dependencies
├── README.md                    # Full documentation
├── HARDWARE_WIRING.md          # Hardware guide
└── QUICK_REFERENCE.md          # This file
```

## Installation
```bash
pip install -r requirements.txt
# or
pip install spidev==3.6
```

## Basic Pin Control

### Set Pin High (Activate)
```python
mcp.set_pin_high('A', 0)      # Port A, Pin 0
```

### Set Pin Low (Deactivate)
```python
mcp.set_pin_low('B', 3)       # Port B, Pin 3
```

### Pulse Pin (Button Press Simulation)
```python
mcp.pulse_pin('A', 0, duration=0.1)  # 100ms pulse
```

### Toggle Pin
```python
new_state = mcp.toggle_pin('A', 5)   # Returns new state
```

## Port Control

### Set Entire Port to Binary Pattern
```python
mcp.set_port('A', 0b10101010)  # 0xAA = alternating pattern
mcp.set_port('A', 0xFF)         # All high
mcp.set_port('A', 0x00)         # All low
```

### Read Port State
```python
state = mcp.get_port_state('A')
print(f"Port A: 0x{state:02X} ({state:08b})")
```

## Matrix Operations

### Initialize Matrix Controller
```python
from mcp23s17_controller import MatrixController

# 4x4 matrix with rows on port A, columns on port B
controller = MatrixController(num_rows=4, num_cols=4,
                             row_port='A', col_port='B')
```

### Press Single Button
```python
controller.press_button(row=1, col=2, duration=0.15)
```

### Press Sequence
```python
sequence = [
    (0, 0), (0, 1), (0, 2), (0, 3),  # First row
    (1, 0), (1, 1), (1, 2), (1, 3),  # Second row
]
controller.press_sequence(sequence, duration=0.1, interval=0.3)
```

### Advanced Matrix Press
```python
# Control row and column pins individually
mcp.pulse_row_column(row=2, col=3, 
                    row_port='A', col_port='B',
                    duration=0.1)
```

## Common Patterns

### Press All Buttons
```python
matrix = 4  # 4x4 matrix
for row in range(matrix):
    for col in range(matrix):
        controller.press_button(row, col, duration=0.05)
```

### Diagonal Pattern
```python
diagonal = [(i, i) for i in range(8)]
controller.press_sequence(diagonal, duration=0.1, interval=0.2)
```

### All Rows Then All Columns
```python
# Press each row
for i in range(4):
    mcp.pulse_pin('A', i, duration=0.1)
    time.sleep(0.3)

# Press each column
for i in range(4):
    mcp.pulse_pin('B', i, duration=0.1)
    time.sleep(0.3)
```

## Configuration

### Custom SPI Bus
```python
# Use SPI bus 1
mcp = MCP23S17(bus=1, device=0)

# Faster SPI clock
mcp = MCP23S17(speed_hz=400000)

# Slower SPI clock (more reliable)
mcp = MCP23S17(speed_hz=50000)
```

### Pin Modes
```python
# Configure pin as output (default)
mcp.configure_pin_mode('A', 0, is_output=True)

# Configure pin as input
mcp.configure_pin_mode('B', 5, is_output=False)

# Read input
input_value = mcp.read_port_input('B')
```

## Timing Reference

### Pulse Durations
```python
mcp.pulse_pin('A', 0, duration=0.05)   # Quick: 50ms
mcp.pulse_pin('A', 0, duration=0.1)    # Normal: 100ms
mcp.pulse_pin('A', 0, duration=0.15)   # Medium: 150ms
mcp.pulse_pin('A', 0, duration=0.5)    # Long: 500ms
```

### Interval Timings
```python
# Quick sequence
controller.press_sequence(buttons, duration=0.05, interval=0.1)

# Normal pace
controller.press_sequence(buttons, duration=0.1, interval=0.3)

# Slow pace (like human typing)
controller.press_sequence(buttons, duration=0.1, interval=0.5)
```

## Error Handling

### Basic Try-Catch
```python
try:
    mcp = MCP23S17()
    mcp.pulse_pin('A', 0, duration=0.1)
except Exception as e:
    print(f"Error: {e}")
finally:
    mcp.cleanup()
```

### Validation
```python
# Port must be 'A' or 'B'
# Pin must be 0-7
# Value must be 0-255 (0x00-0xFF)

mcp.set_pin_high('C', 0)       # ValueError: Port must be 'A' or 'B'
mcp.set_pin_high('A', 8)       # ValueError: Pin must be 0-7
mcp.set_port('A', 256)         # ValueError: Value must be 0-255
```

## Logging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Levels
```python
logging.basicConfig(level=logging.DEBUG)    # Everything
logging.basicConfig(level=logging.INFO)     # Major operations
logging.basicConfig(level=logging.WARNING)  # Problems only
logging.basicConfig(level=logging.ERROR)    # Errors only
```

## Byte Operations

### Understanding Binary
```python
# Setting individual bits
value = 0x00
value |= (1 << 0)   # Set bit 0 → 0x01
value |= (1 << 3)   # Set bit 3 → 0x09
value &= ~(1 << 1)  # Clear bit 1

# Port values
0b00000000 = 0x00 = All low
0b11111111 = 0xFF = All high
0b10101010 = 0xAA = Alternating
0b01010101 = 0x55 = Alternating (opposite)
```

## Performance Tips

1. **Reuse MCP object**: Don't create new MCP23S17() each time
2. **Batch operations**: Use `set_port()` instead of multiple pin sets
3. **Minimize SPI speed**: Use 100kHz unless you have a specific reason for higher
4. **Cache state**: Library caches port states automatically

## Troubleshooting Quick Checks

```python
# Test 1: Is SPI working?
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
result = spi.xfer2([0x40, 0x12, 0x00])  # Read GPIO A
print(result)  # Should return 3 bytes

# Test 2: Is MCP23S17 responding?
from mcp23s17_controller import MCP23S17
mcp = MCP23S17()
state = mcp.get_port_state('A')
print(f"Port A: {state}")  # Should read 0x00

# Test 3: Are pins toggling?
mcp.set_port('A', 0xFF)
# Connect multimeter to GPA0 - should read ~3.3V
mcp.set_port('A', 0x00)
# Should read ~0V
```

## Pin Reference

### Port A (Pins 1-8 on MCP23S17)
```
GPA0 = Pin 0
GPA1 = Pin 1
GPA2 = Pin 2
GPA3 = Pin 3
GPA4 = Pin 4
GPA5 = Pin 5
GPA6 = Pin 6
GPA7 = Pin 7
```

### Port B (Pins 10-17 on MCP23S17)
```
GPB0 = Pin 0
GPB1 = Pin 1
GPB2 = Pin 2
GPB3 = Pin 3
GPB4 = Pin 4
GPB5 = Pin 5
GPB6 = Pin 6
GPB7 = Pin 7
```

## Register Reference

```python
# Input/Output direction
IODIRA = 0x00   # Port A direction (1=input, 0=output)
IODIRB = 0x01   # Port B direction

# GPIO output values
GPIOA = 0x12    # Port A GPIO register
GPIOB = 0x13    # Port B GPIO register

# Pull-up resistors
GPPUA = 0x0C    # Port A pull-ups
GPPUB = 0x0D    # Port B pull-ups
```

## Safe Shutdown

```python
# Always clean up on exit
try:
    # ... your code ...
    controller.press_button(0, 0)
finally:
    mcp.cleanup()

# Or use context manager pattern (if implemented)
with MCP23S17() as mcp:
    mcp.pulse_pin('A', 0)
    # Auto cleanup on exit
```

## Example: Button Press Sequence

```python
from mcp23s17_controller import MatrixController
import time

controller = MatrixController(num_rows=4, num_cols=4)

# Simulate entering a code: 1-2-3-4
code = [(0, 0), (0, 1), (0, 2), (0, 3)]

try:
    for i, (row, col) in enumerate(code):
        print(f"Entering: {i+1}")
        controller.press_button(row, col, duration=0.1)
        time.sleep(0.5)
    print("Code entered!")
except KeyboardInterrupt:
    print("Interrupted")
finally:
    controller.cleanup()
```

## Multiple Chips

```python
# Two MCP23S17 chips on same bus
mcp1 = MCP23S17(device=0, chip_select=0)
mcp2 = MCP23S17(device=0, chip_select=1)

# Use independently
mcp1.set_pin_high('A', 0)
mcp2.set_pin_high('A', 0)

# Clean up both
mcp1.cleanup()
mcp2.cleanup()
```

## Common Mistakes

### ❌ Forgetting Cleanup
```python
mcp = MCP23S17()
mcp.pulse_pin('A', 0)
# Missing: mcp.cleanup()  ← SPI stays open!
```

### ✓ Correct Pattern
```python
mcp = MCP23S17()
try:
    mcp.pulse_pin('A', 0)
finally:
    mcp.cleanup()
```

### ❌ Wrong Port String
```python
mcp.set_pin_high('C', 0)  # ❌ Should be 'A' or 'B'
```

### ✓ Correct Port
```python
mcp.set_pin_high('A', 0)  # ✓ Valid
mcp.set_pin_high('B', 0)  # ✓ Valid
```

## Resources

- **Datasheet**: https://ww1.microchip.com/en-US/product/mcp23s17
- **Examples**: See `examples.py`
- **Full Docs**: See `README.md`
- **Hardware**: See `HARDWARE_WIRING.md`

---

**Quick Links:**
- Basic Usage: See "Basic Pin Control"
- Matrix Control: See "Matrix Operations"
- Examples: Run `python examples.py`
- Help: Set `logging.basicConfig(level=logging.DEBUG)`
