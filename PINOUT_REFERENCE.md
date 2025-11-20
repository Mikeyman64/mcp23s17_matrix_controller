# MCP23S17-E/SS 28-pin DIP Wiring Summary

This document provides a quick reference for the MCP23S17-E/SS 28-pin DIP package wiring.

## Chip Pinout (28-pin DIP)

```
         +---+
    B0  |1 ·28| A7
    B1  |2  27| A6
    B2  |3  26| A5
    B3  |4  25| A4
    B4  |5  24| A3
    B5  |6  23| A2
    B6  |7  22| A1
    B7  |8  21| A0
   VDD  |9  20| INTA
   VSS  |10 19| INTB
   /CS  |11 18| /RESET
   SCK  |12 17| A2 (addr)
    SI  |13 16| A1 (addr)
    SO  |14 15| A0 (addr)
         +---+
```

## Wiring Quick Reference

### Power
- **Pin 9 (VDD)**: Connect to 3.3V through 0.1µF decoupling capacitor
- **Pin 10 (VSS)**: Connect to GND

### SPI Bus (Raspberry Pi 5)
| Signal | MCP Pin | RPi GPIO | RPi Pin |
|--------|---------|----------|---------|
| SCK    | 12      | GPIO 11  | 23      |
| SI     | 13      | GPIO 10  | 19      |
| SO     | 14      | GPIO 9   | 21      |
| /CS    | 11      | GPIO 8   | 24      |

### Control Signals
- **Pin 18 (/RESET)**: Connect to 3.3V (pull high)
- **Pin 19 (INTB)**: Leave floating or connect to GPIO for interrupts
- **Pin 20 (INTA)**: Leave floating or connect to GPIO for interrupts

### Address Selection (for single chip)
- **Pin 15 (A0)**: Connect to GND
- **Pin 16 (A1)**: Connect to GND
- **Pin 17 (A2)**: Connect to GND
- **Chip Address**: 0x20 (when all address pins are GND)

### GPIO Ports

**Port B (Pins 1-8)**: Typically for row control
```
Pin 1  = GPB0
Pin 2  = GPB1
Pin 3  = GPB2
Pin 4  = GPB3
Pin 5  = GPB4
Pin 6  = GPB5
Pin 7  = GPB6
Pin 8  = GPB7
```

**Port A (Pins 21-28)**: Typically for column control
```
Pin 21 = GPA0
Pin 22 = GPA1
Pin 23 = GPA2
Pin 24 = GPA3
Pin 25 = GPA4
Pin 26 = GPA5
Pin 27 = GPA6
Pin 28 = GPA7
```

## BJT Base Drive Circuit

For each GPIO pin driving a BJT transistor:

```
MCP23S17 GPIO ──[10kΩ]── BJT Base
                          BJT Collector ──[10kΩ pull-up]── VCC
                          BJT Emitter ── GND
```

## Example: 4×4 Matrix Wiring

### Port B (Rows 0-3)
```
Pin 1 (GPB0) ──[10kΩ]── BJT Row0 Base
Pin 2 (GPB1) ──[10kΩ]── BJT Row1 Base
Pin 3 (GPB2) ──[10kΩ]── BJT Row2 Base
Pin 4 (GPB3) ──[10kΩ]── BJT Row3 Base
```

### Port A (Columns 0-3)
```
Pin 21 (GPA0) ──[10kΩ]── BJT Col0 Base
Pin 22 (GPA1) ──[10kΩ]── BJT Col1 Base
Pin 23 (GPA2) ──[10kΩ]── BJT Col2 Base
Pin 24 (GPA3) ──[10kΩ]── BJT Col3 Base
```

## Multi-chip Configuration

To use multiple MCP23S17 chips on the same SPI bus, tie address pins differently:

| Chip | A2  | A1  | A0  | Address | /CS Pin |
|------|-----|-----|-----|---------|---------|
| 1    | GND | GND | GND | 0x20    | GPIO 8  |
| 2    | GND | GND | 3V3 | 0x21    | GPIO 7  |
| 3    | GND | 3V3 | GND | 0x22    | GPIO 8  |
| 4    | GND | 3V3 | 3V3 | 0x23    | GPIO 7  |

Note: Use different /CS GPIO pins if using the same SPI device (SPI0)

## Decoupling Capacitor

Place a 0.1µF ceramic capacitor as close as possible to the chip:
```
      VDD (Pin 9)
        │
       ┌┴┐
       │ │ 0.1µF
       └┬┘
        │
      VSS (Pin 10)
```

## Safety Checks

Before power-on:
1. ✓ VDD and VSS properly connected
2. ✓ SPI signals connected correctly
3. ✓ /RESET tied to VDD
4. ✓ Address pins configured
5. ✓ All base resistors 10kΩ
6. ✓ Pull-up resistors on matrix lines
7. ✓ No short circuits
8. ✓ Decoupling capacitor in place

## Testing with Python

```python
from mcp23s17_controller import MCP23S17

# Initialize (assumes address = 0x20, all address pins to GND)
mcp = MCP23S17(bus=0, device=0, chip_select=0)

# Test Port B (rows)
mcp.set_port('B', 0xFF)  # All rows on
mcp.set_port('B', 0x00)  # All rows off

# Test Port A (columns)
mcp.set_port('A', 0xFF)  # All columns on
mcp.set_port('A', 0x00)  # All columns off

mcp.cleanup()
```

## Common Issues

### No Communication
- Check SPI enabled: `sudo raspi-config`
- Verify /CS connects to correct GPIO
- Confirm all SPI signals routed correctly
- Test with logic analyzer on SPI lines

### Pins Not Switching
- Check 10kΩ base resistors
- Verify BJT connections (Base, Collector, Emitter)
- Confirm /RESET is pulled high
- Check VDD and VSS continuity

### Intermittent Operation
- Add 0.1µF decoupling cap near VDD/VSS
- Reduce SPI speed to 100kHz
- Check for loose connections
- Verify pull-up resistor values

## Useful Commands

```bash
# List SPI devices
ls -la /dev/spidev*

# Check GPIO pins
gpio readall | grep "11\|8\|9\|10"

# Monitor SPI with logic analyzer
# Connect probe to pins 12 (SCK), 13 (SI), 14 (SO), 11 (/CS)
```

---

**Quick Wiring Checklist for 4×4 Matrix**

- [ ] VDD (Pin 9) → 3.3V with 0.1µF cap to GND
- [ ] VSS (Pin 10) → GND
- [ ] SCK (Pin 12) → RPi GPIO 11
- [ ] SI (Pin 13) → RPi GPIO 10
- [ ] SO (Pin 14) → RPi GPIO 9
- [ ] /CS (Pin 11) → RPi GPIO 8
- [ ] /RESET (Pin 18) → 3.3V
- [ ] A0, A1, A2 (Pins 15-17) → GND
- [ ] 4 x 10kΩ resistors on Port B (Pins 1-4) for row BJTs
- [ ] 4 x 10kΩ resistors on Port A (Pins 21-24) for column BJTs
- [ ] 8 BJT transistors configured as switches
- [ ] All connections solid (no loose wires)
