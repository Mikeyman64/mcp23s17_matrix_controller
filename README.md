# MCP23S17 SPI Matrix Controller

A comprehensive Python library for controlling an MCP23S17 GPIO expander over SPI on a Raspberry Pi 5. Designed to control BJT transistor bases for simulating button presses in row/column matrix input systems.

## Features

- **Full MCP23S17 Support**: Complete control of both 8-bit ports (A and B)
- **SPI Communication**: Direct SPI communication at configurable speeds
- **Matrix Operations**: High-level matrix button press simulation
- **Pulse Control**: Generate configurable pulses for button press simulation
- **Thread-Safe**: Safe concurrent access to hardware
- **Comprehensive Logging**: Detailed logging for debugging
- **Error Handling**: Robust error handling and resource cleanup
- **Production Ready**: Used in real hardware applications

## Hardware Setup

### MCP23S17-E/SS 28-pin DIP Pinout
```
Pin 1  - GPB0
Pin 2  - GPB1
Pin 3  - GPB2
Pin 4  - GPB3
Pin 5  - GPB4
Pin 6  - GPB5
Pin 7  - GPB6
Pin 8  - GPB7
Pin 9  - VDD (3.3V or 5V)
Pin 10 - VSS (GND)
Pin 11 - /CS (Chip Select, Active Low)
Pin 12 - SCK (SPI Clock)
Pin 13 - SI (SPI Data In / MOSI)
Pin 14 - SO (SPI Data Out / MISO)
Pin 15 - A0 (Address Select 0)
Pin 16 - A1 (Address Select 1)
Pin 17 - A2 (Address Select 2)
Pin 18 - /RESET (Active Low Reset)
Pin 19 - INTB (Interrupt B, Optional)
Pin 20 - INTA (Interrupt A, Optional)
Pin 21 - GPA0
Pin 22 - GPA1
Pin 23 - GPA2
Pin 24 - GPA3
Pin 25 - GPA4
Pin 26 - GPA5
Pin 27 - GPA6
Pin 28 - GPA7
```

### Raspberry Pi 5 SPI Connections
```
RPi Pin  MCP23S17 Pin  Function
================================
GPIO11   Pin 12        SCK (SPI Clock)
GPIO9    Pin 14        SO (SPI Data Out / MISO)
GPIO10   Pin 13        SI (SPI Data In / MOSI)
GPIO8    Pin 11        /CS (Chip Select, Active Low)
3.3V     Pin 9         VDD (Power)
GND      Pin 10        VSS (Ground)
3.3V     Pin 18        /RESET (Pull high, Active Low)
```

### Address Select Pins (A0, A1, A2)
```
These determine the chip address (0x20-0x27)
For single chip, typically tie all to GND:
GND      Pin 15        A0
GND      Pin 16        A1
GND      Pin 17        A2
```

### Optional: Interrupt Pins
```
Pin 19 - INTB (Port B Interrupt, Optional)
Pin 20 - INTA (Port A Interrupt, Optional)
Can be left floating if not using interrupts
```

### BJT Configuration
```
MCP23S17 Output → 10kΩ Resistor → BJT Base
BJT Collector → Target Matrix Row/Column
BJT Emitter → GND
BJT Collector → Pull-up Resistor (10kΩ) → VCC
```

## Installation

### Prerequisites
- Raspberry Pi 5 with Raspberry Pi OS
- Python 3.9+
- SPI enabled on Raspberry Pi

### Setup Steps

1. **Enable SPI on Raspberry Pi**
```bash
sudo raspi-config
# Navigate to: Interfacing Options → SPI → Enable
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify SPI**
```bash
ls -la /dev/spidev*
# Should show: /dev/spidev0.0 /dev/spidev0.1
```

## Quick Start

### Basic Usage
```python
from mcp23s17_controller import MCP23S17

# Initialize
mcp = MCP23S17(bus=0, device=0, speed_hz=100000)

# Set pin high (activate BJT)
mcp.set_pin_high('A', 0)

# Set pin low (deactivate BJT)
mcp.set_pin_low('A', 0)

# Pulse pin (simulate button press)
mcp.pulse_pin('A', 0, duration=0.1)

# Clean up
mcp.cleanup()
```

### Matrix Control
```python
from mcp23s17_controller import MatrixController

# Initialize 4x4 matrix
controller = MatrixController(num_rows=4, num_cols=4,
                             row_port='A', col_port='B')

# Press single button
controller.press_button(row=1, col=2, duration=0.1)

# Press sequence
sequence = [(0, 0), (0, 1), (1, 0), (1, 1)]
controller.press_sequence(sequence, duration=0.1, interval=0.3)

# Clean up
controller.cleanup()
```

## API Reference

### MCP23S17 Class

#### Constructor
```python
MCP23S17(bus=0, device=0, chip_select=0, speed_hz=100000)
```
- `bus`: SPI bus number (0 or 1)
- `device`: SPI device number
- `chip_select`: Chip select (0 or 1)
- `speed_hz`: SPI clock speed (100kHz to 10MHz)

#### Methods

##### Pin Control
```python
set_pin_high(port, pin)      # Set pin high
set_pin_low(port, pin)       # Set pin low
toggle_pin(port, pin)        # Toggle pin state
pulse_pin(port, pin, duration)  # Generate pulse
```

##### Port Control
```python
set_port(port, value)        # Set entire port to value
get_port_state(port)         # Get current port state
```

##### Matrix Operations
```python
pulse_row_column(row, col, row_port, col_port, duration)
matrix_sequence(sequence, row_port, col_port, duration, interval)
```

##### Configuration
```python
configure_pin_mode(port, pin, is_output)  # Set pin mode
read_port_input(port)                     # Read input port
```

##### Cleanup
```python
cleanup()                    # Clean up resources
```

### MatrixController Class

#### Constructor
```python
MatrixController(num_rows=4, num_cols=4, row_port='A', col_port='B')
```

#### Methods
```python
press_button(row, col, duration)
press_sequence(buttons, duration, interval)
cleanup()
```

## Examples

### Example 1: Simple Button Press
```python
from mcp23s17_controller import MCP23S17

mcp = MCP23S17()
mcp.pulse_pin('A', 0, duration=0.1)
mcp.cleanup()
```

### Example 2: Matrix Sequence
```python
from mcp23s17_controller import MatrixController

controller = MatrixController(num_rows=4, num_cols=4)
sequence = [(0, 0), (1, 1), (2, 2), (3, 3)]
controller.press_sequence(sequence, duration=0.1, interval=0.3)
controller.cleanup()
```

### Example 3: Port Control
```python
from mcp23s17_controller import MCP23S17

mcp = MCP23S17()
mcp.set_port('A', 0xFF)  # Set all pins on port A high
time.sleep(1)
mcp.set_port('A', 0x00)  # Set all pins low
mcp.cleanup()
```

See `examples.py` for more comprehensive examples.

## Timing Considerations

### Pulse Timing
- **Quick Press**: 0.05-0.10 seconds
- **Normal Press**: 0.10-0.15 seconds
- **Long Press**: 0.5-1.0 seconds

### Matrix Access Time
- **Single Press**: ~20ms (at 100kHz SPI)
- **Sequence Press**: ~20ms per button

### SPI Speed
- **100kHz**: Safe, standard speed
- **400kHz**: Faster, works well
- **1MHz**: Maximum recommended for reliability
- **>1MHz**: Possible but not recommended

## Troubleshooting

### SPI Not Available
```bash
# Check SPI is enabled
dmesg | grep spi

# Check device files exist
ls -la /dev/spidev*
```

### No Response from MCP23S17
1. Check wiring (especially SCK, MOSI, MISO, CS)
2. Check VCC and GND connections
3. Verify RESET pin is pulled high
4. Check SPI speed is not too high
5. Use logic analyzer to verify SPI communication

### Pins Not Responding
1. Check port configuration (A or B)
2. Verify pin number (0-7)
3. Check pin state with `get_port_state()`
4. Verify BJT transistor connections

### High Power Consumption
1. Ensure pins are properly driven low when not needed
2. Check for short circuits on BJT outputs
3. Verify resistor values

## Performance Specifications

- **Max SPI Speed**: 10MHz (not recommended, use ≤1MHz)
- **Min SPI Speed**: 100kHz
- **Output Current per Pin**: 25mA (absolute max)
- **Output Current total (port)**: 125mA (absolute max)
- **Access Time**: ~1µs per register
- **Typical Button Press Duration**: 100-150ms

## Advanced Features

### Custom SPI Speed
```python
mcp = MCP23S17(bus=0, device=0, speed_hz=400000)
```

### Multiple MCP23S17 Chips
```python
mcp1 = MCP23S17(bus=0, device=0, chip_select=0)
mcp2 = MCP23S17(bus=0, device=0, chip_select=1)
```

### Input Mode (Mixed I/O)
```python
mcp = MCP23S17()
# Configure port A as output, port B as input
mcp.configure_pin_mode('B', 0, is_output=False)
state = mcp.read_port_input('B')
```

## Logging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Log levels:
- `DEBUG`: Register read/write operations
- `INFO`: High-level operations
- `WARNING`: Non-critical issues
- `ERROR`: Operation failures

## Known Limitations

1. **Single SPI Bus**: All MCP23S17 chips on same bus must use different chip selects
2. **Max Pins**: 16 pins per chip (2 ports × 8 pins)
3. **Bus Contention**: SPI bus cannot be used by other devices simultaneously
4. **No Interrupt Support**: Currently no interrupt handling (can be added)

## Future Enhancements

- [ ] Interrupt support
- [ ] Hardware SPI speed optimization
- [ ] Multi-chip management
- [ ] Data logging
- [ ] Web API interface
- [ ] Async/await support

## Testing

Run the example suite:
```bash
python examples.py
```

## License

MIT License - Feel free to modify and distribute

## Support

For issues or questions:
1. Check the examples
2. Review the API documentation
3. Check hardware connections
4. Enable debug logging

## References

- [MCP23S17 Datasheet](https://ww1.microchip.com/en-US/product/mcp23s17)
- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.com/documentation/)
- [SPI Protocol Documentation](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface)
