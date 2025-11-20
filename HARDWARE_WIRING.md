# MCP23S17 Hardware Wiring Guide

## Overview
This guide shows how to connect the MCP23S17 to a Raspberry Pi 5 and wire BJT transistors in a **common-emitter matrix configuration** to simulate button presses.

## BJT Matrix Configuration (Your Setup)

Your hardware uses a **dedicated BJT per button** configuration where:
- Each of the 12 buttons has its own BJT transistor
- Each BJT base is controlled by a dedicated MCP23S17 GPIO pin
- When a BJT base is activated, it shorts the corresponding button's row and column together

### 3×4 Keypad Layout (Your Actual Wiring)

```
           COL1    COL2    COL3    COL4
            │       │       │       │
ROW1 ───────+───┬───+───┬───+───┬───+
            │   │   │   │   │   │   │
          BJT5 BJT6 BJT7 BJT8 (buttons 1,2,3,CALL)
            │   │   │   │
            
ROW2 ───────+───┬───+───┬───+───┬───+
            │   │   │   │   │   │   │
          BJT9 BJT10 BJT11 BJT12 (buttons 4,5,6,0)
            │   │   │   │
            
ROW3 ───────+───┬───+───┬───+───┬───+
            │   │   │   │   │   │   │
          BJT1 BJT2 BJT3 BJT4 (buttons 7,8,9,CLR)
```

### Complete GPIO to Button Mapping

**MCP23S17 Port B (GPB0-3) → ROW3 Buttons:**
| MCP Pin | GPIO   | BJT | Button | Position |
|---------|--------|-----|--------|----------|
| 1       | GPB0   | 1   | 7      | ROW3/COL1 |
| 2       | GPB1   | 2   | 8      | ROW3/COL2 |
| 3       | GPB2   | 3   | 9      | ROW3/COL3 |
| 4       | GPB3   | 4   | CLR    | ROW3/COL4 |

**MCP23S17 Port A (GPA0-3) → ROW1 Buttons:**
| MCP Pin | GPIO   | BJT | Button | Position |
|---------|--------|-----|--------|----------|
| 21      | GPA0   | 5   | 1      | ROW1/COL1 |
| 22      | GPA1   | 6   | 2      | ROW1/COL2 |
| 23      | GPA2   | 7   | 3      | ROW1/COL3 |
| 24      | GPA3   | 8   | CALL   | ROW1/COL4 |

**MCP23S17 Port A (GPA4-7) → ROW2 Buttons:**
| MCP Pin | GPIO   | BJT | Button | Position |
|---------|--------|-----|--------|----------|
| 25      | GPA4   | 9   | 4      | ROW2/COL1 |
| 26      | GPA5   | 10  | 5      | ROW2/COL2 |
| 27      | GPA6   | 11  | 6      | ROW2/COL3 |
| 28      | GPA7   | 12  | 0      | ROW2/COL4 |

### Button Press Mechanism

To press any button:
1. Activate the corresponding MCP23S17 GPIO pin
2. That pin drives the BJT base through a 10kΩ resistor
3. BJT turns ON, connecting its row line to its column line
4. The button press is detected at that row/column intersection

**Example: Press Button 1 (ROW1/COL1)**
- Activate MCP23S17 GPA0 (Pin 21)
- BJT5 base activates
- BJT5 emitter (tied to ROW1) connects to BJT5 collector (tied to COL1)
- Button press detected!

## Raspberry Pi 5 SPI Pinout

```
Raspberry Pi 5 40-pin GPIO Header (Top View)
============================================

3.3V  5V   GND  GND  BCM14  BCM15
  1    2    3    4     8      10

                 GPIO Layout
    ┌─────────────────────────────┐
    │ P1  P2  P3  P4  P5  P6      │
    │ 3V3 5V  GND GND BCM14 BCM15│  Pin 1-2, 3-4, 5-6, etc.
    │                             │
    │ P7  P8  P9  P10 P11 P12     │
    │ BCM17 BCM27 GND BCM22 BCM10 BCM9│
    │                             │
    │ P13 P14 P15 P16 P17 P18     │
    │ GND GND BCM23 BCM24 GND BCM25│
    │                             │
    │ P19 P20 P21 P22 P23 P24     │
    │ BCM8 GND BCM7 CE0 CE1 GND   │
    │                             │
    │ ... (more pins)             │
    └─────────────────────────────┘

```

## SPI Bus (Bus 0) Connections

| Raspberry Pi Pin | GPIO | Function | MCP23S17 Pin |
|------------------|------|----------|--------------|
| 19               | 10   | MOSI     | 13 (SI)      |
| 21               | 9    | MISO     | 14 (SO)      |
| 23               | 11   | SCK      | 12 (SCK)     |
| 24               | 8    | /CS      | 11 (/CS)     |
| 1                | -    | 3.3V     | 9 (VDD)      |
| 6 (or any)       | -    | GND      | 10 (VSS)     |
| 1                | -    | 3.3V     | 18 (/RESET)  |
| 6 (or any)       | -    | GND      | 15 (A0)      |
| 6 (or any)       | -    | GND      | 16 (A1)      |
| 6 (or any)       | -    | GND      | 17 (A2)      |

## Wiring Diagram

### Complete Setup with BJTs

```
Raspberry Pi 5                      MCP23S17-E/SS (28-pin)
════════════════                   ═══════════════════════════
Pin 1 (3.3V) ──────────────────┬─→ Pin 9 (VDD)
                               │
                               ├─→ Pin 18 (/RESET)
                               │
                               ├─→ Pin 15 (A0)
                               │
                               ├─→ Pin 16 (A1)
                               │
                               └─→ Pin 17 (A2)

Pin 6 (GND) ───────────────────┬─→ Pin 10 (VSS)

Pin 23 (BCM11/SCK) ────────────→ Pin 12 (SCK)
Pin 19 (BCM10/MOSI) ───────────→ Pin 13 (SI)
Pin 21 (BCM9/MISO) ←───────────→ Pin 14 (SO)
Pin 24 (BCM8/CS) ──────────────→ Pin 11 (/CS)


MCP23S17 GPIO Pins              BJT Transistor Circuit
═══════════════════            ═════════════════════════

Port B (Pins 1-8, Row Control):
Pin 1 (GPB0) ──[10kΩ]──→ BJT1 Base
Pin 2 (GPB1) ──[10kΩ]──→ BJT2 Base
Pin 3 (GPB2) ──[10kΩ]──→ BJT3 Base
Pin 4 (GPB3) ──[10kΩ]──→ BJT4 Base
...
Pin 8 (GPB7) ──[10kΩ]──→ BJT8 Base


Port A (Pins 21-28, Column Control):
Pin 21 (GPA0) ──[10kΩ]──→ BJT9 Base
Pin 22 (GPA1) ──[10kΩ]──→ BJT10 Base
Pin 23 (GPA2) ──[10kΩ]──→ BJT11 Base
Pin 24 (GPA3) ──[10kΩ]──→ BJT12 Base
...
Pin 28 (GPA7) ──[10kΩ]──→ BJT16 Base


BJT Circuit Details (for each BJT):
═══════════════════════════════════

         VCC (3.3V or 5V)
             │
             │
          [10kΩ] Pull-up
             │
             │
    ┌────────┴────────┐
    │   Row/Col Pin   │  (from matrix input chip)
    │   (Collector)   │
    │                 │
    │   BJT Trans.    │
    │   (NPN 2N3904)  │
    │                 │
    │   (Base) ←──[10kΩ]─ MCP23S17 GPIO
    │   (Emitter)     │
    │                 │
    └────────┬────────┘
             │
            GND

```

## Component List

For a 4×4 Matrix System:

| Component | Quantity | Notes |
|-----------|----------|-------|
| MCP23S17 | 1 | SPI GPIO Expander |
| BJT (2N3904) | 8 | NPN Transistors (4 rows + 4 cols) |
| Resistor 10kΩ | 16 | 8 base resistors + 8 pull-ups |
| Capacitor 0.1µF | 1 | Decoupling on MCP23S17 VCC |
| Breadboard | 1 | For prototyping |
| Jumper Wires | 50+ | Various connections |

## Decoupling Circuit

Place close to MCP23S17:

```
      ┌─────────┐
3.3V ─┤         ├─ GND
      │ 0.1µF   │
      │ Cap.    │
      └─────────┘
```

## Step-by-Step Wiring

### 1. Power Connections
```
Step 1: Connect VDD
  Raspberry Pi Pin 1 (3.3V) → MCP23S17 Pin 9 (VDD)
  Add 0.1µF capacitor between VDD and VSS near MCP23S17

Step 2: Connect VSS (Ground)
  Raspberry Pi Pin 6 (GND) → MCP23S17 Pin 10 (VSS)
  Also connect to all BJT emitters
```

### 2. SPI Connections
```
Step 3: Connect SCK
  Raspberry Pi Pin 23 (BCM11) → MCP23S17 Pin 12 (SCK)

Step 4: Connect MOSI (SI)
  Raspberry Pi Pin 19 (BCM10) → MCP23S17 Pin 13 (SI)

Step 5: Connect MISO (SO)
  Raspberry Pi Pin 21 (BCM9) → MCP23S17 Pin 14 (SO)

Step 6: Connect /CS (Chip Select)
  Raspberry Pi Pin 24 (BCM8) → MCP23S17 Pin 11 (/CS)

Step 7: Connect /RESET
  Raspberry Pi Pin 1 (3.3V) → MCP23S17 Pin 18 (/RESET)

Step 8: Address Select Pins (for single chip, tie to GND)
  Raspberry Pi Pin 6 (GND) → MCP23S17 Pin 15 (A0)
  Raspberry Pi Pin 6 (GND) → MCP23S17 Pin 16 (A1)
  Raspberry Pi Pin 6 (GND) → MCP23S17 Pin 17 (A2)
```

### 3. BJT Base Resistors (10kΩ each)

Port B (Row BJTs, Pins 1-8):
```
MCP23S17 Pin 1 (GPB0) ──[10kΩ]── BJT1 Base
MCP23S17 Pin 2 (GPB1) ──[10kΩ]── BJT2 Base
MCP23S17 Pin 3 (GPB2) ──[10kΩ]── BJT3 Base
MCP23S17 Pin 4 (GPB3) ──[10kΩ]── BJT4 Base
```

Port A (Column BJTs, Pins 21-28):
```
MCP23S17 Pin 21 (GPA0) ──[10kΩ]── BJT5 Base
MCP23S17 Pin 22 (GPA1) ──[10kΩ]── BJT6 Base
MCP23S17 Pin 23 (GPA2) ──[10kΩ]── BJT7 Base
MCP23S17 Pin 24 (GPA3) ──[10kΩ]── BJT8 Base
```

### 4. BJT Collector Connections

Each BJT collector connects to a row or column line of the matrix input chip:
```
BJT1 Collector → Matrix Row 0
BJT2 Collector → Matrix Row 1
BJT3 Collector → Matrix Row 2
BJT4 Collector → Matrix Row 3

BJT5 Collector → Matrix Col 0
BJT6 Collector → Matrix Col 1
BJT7 Collector → Matrix Col 2
BJT8 Collector → Matrix Col 3
```

### 5. Pull-up Resistors

Each matrix line needs a pull-up resistor (10kΩ):
```
Matrix Line ──[10kΩ]── VCC (of matrix input chip)
                  │
              BJT Collector
                  │
                GND
```

## Verification Checklist

- [ ] All SPI pins connected (MOSI, MISO, SCK, CS)
- [ ] VCC connected to Pin 18 with 0.1µF decoupling cap
- [ ] GND connected to Pin 9
- [ ] RESET tied to VCC (Pin 23 to Pin 1)
- [ ] All base resistors installed (10kΩ)
- [ ] All BJT emitters connected to GND
- [ ] All pull-up resistors installed (10kΩ on matrix lines)
- [ ] No short circuits between adjacent pins
- [ ] Wires properly crimped or soldered
- [ ] Breadboard connections are secure

## Testing Connections

### 1. Resistance Checks
```bash
# Measure between pins while powered off
# VCC to GND should not be shorted (infinite resistance through resistors)
# Each base resistor should read approximately 10kΩ
```

### 2. SPI Communication Test
```python
from mcp23s17_controller import MCP23S17
import time

mcp = MCP23S17()

# All pins should turn on then off
mcp.set_port('A', 0xFF)
time.sleep(1)
mcp.set_port('A', 0x00)

mcp.set_port('B', 0xFF)
time.sleep(1)
mcp.set_port('B', 0x00)

mcp.cleanup()
```

### 3. LED Test (Optional)
Add LEDs in series with 1kΩ resistors on BJT collectors to verify switching:
```
BJT Collector ──[1kΩ]── LED ──│→ GND
(LED visible = transistor on)
```

## Common Issues & Solutions

### Issue: No SPI Communication
**Solution:**
1. Check SPI is enabled: `sudo raspi-config`
2. Verify correct pins used
3. Check wiring with multimeter
4. Try slower SPI speed: `speed_hz=100000`

### Issue: Pins Not Responding
**Solution:**
1. Check base resistor values (should be 10kΩ)
2. Verify BJT connections (Base, Collector, Emitter)
3. Test with logic analyzer if available
4. Check VCC and GND continuity

### Issue: Intermittent Operation
**Solution:**
1. Add capacitors: 0.1µF on MCP VCC + GND
2. Reduce SPI speed
3. Add ferrite core on SPI wires
4. Use shielded cables if possible

### Issue: BJT Not Switching
**Solution:**
1. Check BJT transistor polarity (Base should be in middle)
2. Verify base current is sufficient (10mA typical for 2N3904)
3. Check collector load (pull-up resistor)
4. Test transistor with manual GPIO first

## Layout Tips

1. **Decoupling**: Place 0.1µF capacitor as close as possible to VCC/GND pins
2. **Trace Length**: Keep SPI traces short and away from power lines
3. **Grounding**: Use star grounding pattern
4. **Resistor Placement**: Base resistors close to BJT bases
5. **Wire Gauge**: Use 22-26 AWG for connections

## Safety Considerations

⚠️ **Important:**
- Raspberry Pi GPIO is 3.3V, not 5V tolerant
- If interfacing with 5V circuits, use level shifters
- BJT collectors should not exceed 5V (use appropriate pull-up voltage)
- Always double-check polarity before applying power
- Use appropriate resistor values to limit current

## Scaling to Larger Matrix

For larger matrices (8×8), use multiple MCP23S17 chips:

```
Chip 1 (CS=0): Controls Rows 0-3
Chip 2 (CS=1): Controls Rows 4-7
Chip 3 (CS=0): Controls Cols 0-3
Chip 4 (CS=1): Controls Cols 4-7

All share same SPI bus (MOSI, MISO, SCK)
Each has separate CS line
```

## Advanced: Level Shifting

If interfacing with 5V circuits, use level shifter IC (e.g., TXS0108E):

```
MCP23S17 (3.3V) ── Level Shifter ── 5V Circuit
                  └─ Bidirectional if needed
```

---

**Always verify connections before powering on!**
