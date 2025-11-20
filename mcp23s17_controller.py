"""
MCP23S17 SPI Matrix Controller for Raspberry Pi 5
Controls BJT bases via MCP23S17 GPIO expander to simulate button presses
in a row/column matrix input system.
"""

import spidev
import time
import logging
from typing import List, Tuple, Dict, Optional
from enum import Enum
from dataclasses import dataclass
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCP23S17Register(Enum):
    """MCP23S17 Register addresses"""
    # Address register (for bank A/B selection)
    IODIRA = 0x00
    IODIRB = 0x01
    IPOLA = 0x02
    IPOLB = 0x03
    GPINTENA = 0x04
    GPINTENB = 0x05
    DEFVALA = 0x06
    DEFVALB = 0x07
    INTCONA = 0x08
    INTCONB = 0x09
    IOCONA = 0x0A
    IOCONB = 0x0B
    GPPUA = 0x0C
    GPPUB = 0x0D
    INTFA = 0x0E
    INTFB = 0x0F
    INTCAPA = 0x10
    INTCAPB = 0x11
    GPIOA = 0x12
    GPIOB = 0x13
    OLATA = 0x14
    OLATB = 0x15


@dataclass
class PinConfig:
    """Configuration for a single output pin"""
    port: str  # 'A' or 'B'
    pin: int   # 0-7
    active_high: bool = True
    pulse_duration: float = 0.1  # seconds


class MCP23S17:
    """
    MCP23S17 SPI GPIO Expander Controller
    
    The MCP23S17 is a 16-bit GPIO expander with two 8-bit ports (A and B).
    This class provides high-level control for matrix switching applications.
    """

    def __init__(self, bus: int = 0, device: int = 0, chip_select: int = 0, 
                 speed_hz: int = 100000):
        """
        Initialize MCP23S17 controller
        
        Args:
            bus: SPI bus number (0 or 1 on RPi 5)
            device: SPI device number
            chip_select: Chip select pin (0 or 1)
            speed_hz: SPI clock speed (100kHz to 10MHz, default 100kHz)
        """
        self.spi = spidev.SpiDev()
        self.bus = bus
        self.device = device
        self.chip_select = chip_select
        self.speed_hz = speed_hz
        
        # Cache for port states
        self.port_a_state = 0x00
        self.port_b_state = 0x00
        
        # Track pin configurations
        self.pin_configs: Dict[Tuple[str, int], PinConfig] = {}
        
        try:
            self.spi.open(bus, device)
            self.spi.max_speed_hz = speed_hz
            self.spi.mode = 0  # Mode 0: CPOL=0, CPHA=0
            self.spi.lsb_first = False
            logger.info(f"SPI initialized on bus {bus}, device {device}, "
                       f"speed {speed_hz} Hz")
        except Exception as e:
            logger.error(f"Failed to initialize SPI: {e}")
            raise
        
        # Initialize MCP23S17
        self._initialize_chip()
        
        # Register cleanup
        atexit.register(self.cleanup)

    def _build_command(self, opcode: int, address: int) -> Tuple[int, int]:
        """
        Build MCP23S17 command byte and address byte
        
        Args:
            opcode: 0 for write, 1 for read
            address: Register address
            
        Returns:
            Tuple of (command_byte, address_byte)
        """
        # Command byte: 0x40 (fixed) | (slave_address << 1) | opcode
        command = 0x40 | (self.chip_select << 1) | opcode
        return command, address

    def _write_register(self, register: MCP23S17Register, data: int) -> None:
        """
        Write a single byte to a register
        
        Args:
            register: Register to write to
            data: Data byte to write
        """
        command, address = self._build_command(opcode=0, address=register.value)
        
        try:
            self.spi.writebytes([command, address, data])
            logger.debug(f"Write register {register.name} = 0x{data:02X}")
        except Exception as e:
            logger.error(f"Failed to write register {register.name}: {e}")
            raise

    def _read_register(self, register: MCP23S17Register) -> int:
        """
        Read a single byte from a register
        
        Args:
            register: Register to read from
            
        Returns:
            Data byte read from register
        """
        command, address = self._build_command(opcode=1, address=register.value)
        
        try:
            result = self.spi.xfer2([command, address, 0x00])
            data = result[2]
            logger.debug(f"Read register {register.name} = 0x{data:02X}")
            return data
        except Exception as e:
            logger.error(f"Failed to read register {register.name}: {e}")
            raise

    def _initialize_chip(self) -> None:
        """Initialize MCP23S17 with all pins as outputs"""
        try:
            # Set all pins on port A as outputs (IODIRA = 0x00)
            self._write_register(MCP23S17Register.IODIRA, 0x00)
            
            # Set all pins on port B as outputs (IODIRB = 0x00)
            self._write_register(MCP23S17Register.IODIRB, 0x00)
            
            # Disable pull-ups
            self._write_register(MCP23S17Register.GPPUA, 0x00)
            self._write_register(MCP23S17Register.GPPUB, 0x00)
            
            # Set initial output state to low
            self._write_register(MCP23S17Register.GPIOA, 0x00)
            self._write_register(MCP23S17Register.GPIOB, 0x00)
            
            # Cache initial states
            self.port_a_state = 0x00
            self.port_b_state = 0x00
            
            logger.info("MCP23S17 initialized: All pins set as outputs, logic low")
        except Exception as e:
            logger.error(f"Failed to initialize MCP23S17: {e}")
            raise

    def set_pin_high(self, port: str, pin: int) -> None:
        """
        Set a pin high (activate BJT base)
        
        Args:
            port: 'A' or 'B'
            pin: Pin number 0-7
        """
        if port.upper() not in ['A', 'B']:
            raise ValueError("Port must be 'A' or 'B'")
        if not 0 <= pin <= 7:
            raise ValueError("Pin must be 0-7")
        
        port = port.upper()
        
        if port == 'A':
            self.port_a_state |= (1 << pin)
            self._write_register(MCP23S17Register.GPIOA, self.port_a_state)
            logger.debug(f"Set pin A{pin} HIGH (state: 0x{self.port_a_state:02X})")
        else:
            self.port_b_state |= (1 << pin)
            self._write_register(MCP23S17Register.GPIOB, self.port_b_state)
            logger.debug(f"Set pin B{pin} HIGH (state: 0x{self.port_b_state:02X})")

    def set_pin_low(self, port: str, pin: int) -> None:
        """
        Set a pin low (deactivate BJT base)
        
        Args:
            port: 'A' or 'B'
            pin: Pin number 0-7
        """
        if port.upper() not in ['A', 'B']:
            raise ValueError("Port must be 'A' or 'B'")
        if not 0 <= pin <= 7:
            raise ValueError("Pin must be 0-7")
        
        port = port.upper()
        
        if port == 'A':
            self.port_a_state &= ~(1 << pin)
            self._write_register(MCP23S17Register.GPIOA, self.port_a_state)
            logger.debug(f"Set pin A{pin} LOW (state: 0x{self.port_a_state:02X})")
        else:
            self.port_b_state &= ~(1 << pin)
            self._write_register(MCP23S17Register.GPIOB, self.port_b_state)
            logger.debug(f"Set pin B{pin} LOW (state: 0x{self.port_b_state:02X})")

    def toggle_pin(self, port: str, pin: int) -> bool:
        """
        Toggle a pin state
        
        Args:
            port: 'A' or 'B'
            pin: Pin number 0-7
            
        Returns:
            New pin state (True if high, False if low)
        """
        if port.upper() not in ['A', 'B']:
            raise ValueError("Port must be 'A' or 'B'")
        if not 0 <= pin <= 7:
            raise ValueError("Pin must be 0-7")
        
        port = port.upper()
        
        if port == 'A':
            is_high = bool(self.port_a_state & (1 << pin))
            if is_high:
                self.set_pin_low(port, pin)
            else:
                self.set_pin_high(port, pin)
            return not is_high
        else:
            is_high = bool(self.port_b_state & (1 << pin))
            if is_high:
                self.set_pin_low(port, pin)
            else:
                self.set_pin_high(port, pin)
            return not is_high

    def set_port(self, port: str, value: int) -> None:
        """
        Set entire port to a byte value
        
        Args:
            port: 'A' or 'B'
            value: 8-bit value to write
        """
        if port.upper() not in ['A', 'B']:
            raise ValueError("Port must be 'A' or 'B'")
        if not 0 <= value <= 0xFF:
            raise ValueError("Value must be 0-255")
        
        port = port.upper()
        
        if port == 'A':
            self.port_a_state = value
            self._write_register(MCP23S17Register.GPIOA, value)
            logger.info(f"Set port A to 0x{value:02X}")
        else:
            self.port_b_state = value
            self._write_register(MCP23S17Register.GPIOB, value)
            logger.info(f"Set port B to 0x{value:02X}")

    def get_port_state(self, port: str) -> int:
        """
        Get current port state
        
        Args:
            port: 'A' or 'B'
            
        Returns:
            8-bit port state
        """
        if port.upper() not in ['A', 'B']:
            raise ValueError("Port must be 'A' or 'B'")
        
        port = port.upper()
        
        if port == 'A':
            return self.port_a_state
        else:
            return self.port_b_state

    def pulse_pin(self, port: str, pin: int, duration: float = 0.1) -> None:
        """
        Generate a pulse on a pin (HIGH then LOW after duration)
        Simulates a button press
        
        Args:
            port: 'A' or 'B'
            pin: Pin number 0-7
            duration: Pulse duration in seconds
        """
        logger.info(f"Pulsing pin {port}{pin} for {duration}s")
        self.set_pin_high(port, pin)
        time.sleep(duration)
        self.set_pin_low(port, pin)

    def pulse_row_column(self, row: int, col: int, row_port: str = 'A',
                        col_port: str = 'B', duration: float = 0.1) -> None:
        """
        Activate a specific row/column intersection (matrix button press)
        
        Args:
            row: Row number (0-7)
            col: Column number (0-7)
            row_port: Port for row control ('A' or 'B')
            col_port: Port for column control ('A' or 'B')
            duration: Pulse duration in seconds
        """
        logger.info(f"Pressing matrix [{row}][{col}] for {duration}s")
        
        self.set_pin_high(row_port, row)
        self.set_pin_high(col_port, col)
        time.sleep(duration)
        self.set_pin_low(row_port, row)
        self.set_pin_low(col_port, col)

    def matrix_sequence(self, sequence: List[Tuple[int, int]], 
                       row_port: str = 'A', col_port: str = 'B',
                       duration: float = 0.1, interval: float = 0.2) -> None:
        """
        Execute a sequence of matrix button presses
        
        Args:
            sequence: List of (row, col) tuples
            row_port: Port for row control
            col_port: Port for column control
            duration: Pulse duration per press
            interval: Time between presses
        """
        logger.info(f"Executing matrix sequence of {len(sequence)} presses")
        
        for i, (row, col) in enumerate(sequence):
            logger.info(f"Press {i+1}/{len(sequence)}: [{row}][{col}]")
            self.pulse_row_column(row, col, row_port, col_port, duration)
            
            if i < len(sequence) - 1:
                time.sleep(interval)

    def read_port_input(self, port: str) -> int:
        """
        Read input from a port (if configured as input)
        
        Args:
            port: 'A' or 'B'
            
        Returns:
            8-bit input value
        """
        if port.upper() not in ['A', 'B']:
            raise ValueError("Port must be 'A' or 'B'")
        
        port = port.upper()
        
        if port == 'A':
            return self._read_register(MCP23S17Register.GPIOA)
        else:
            return self._read_register(MCP23S17Register.GPIOB)

    def configure_pin_mode(self, port: str, pin: int, is_output: bool = True) -> None:
        """
        Configure a pin as input or output
        
        Args:
            port: 'A' or 'B'
            pin: Pin number 0-7
            is_output: True for output, False for input
        """
        if port.upper() not in ['A', 'B']:
            raise ValueError("Port must be 'A' or 'B'")
        if not 0 <= pin <= 7:
            raise ValueError("Pin must be 0-7")
        
        port = port.upper()
        register = MCP23S17Register.IODIRA if port == 'A' else MCP23S17Register.IODIRB
        
        current = self._read_register(register)
        
        if is_output:
            current &= ~(1 << pin)
        else:
            current |= (1 << pin)
        
        self._write_register(register, current)
        logger.info(f"Configured pin {port}{pin} as {'output' if is_output else 'input'}")

    def cleanup(self) -> None:
        """Clean up and close SPI connection"""
        try:
            # Set all outputs to low before closing
            self._write_register(MCP23S17Register.GPIOA, 0x00)
            self._write_register(MCP23S17Register.GPIOB, 0x00)
            self.spi.close()
            logger.info("MCP23S17 cleaned up and SPI closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class MatrixController:
    """
    High-level matrix controller for row/column input switching
    Manages multiple row and column pins for matrix scanning
    """

    def __init__(self, num_rows: int = 4, num_cols: int = 4,
                 row_port: str = 'A', col_port: str = 'B'):
        """
        Initialize matrix controller
        
        Args:
            num_rows: Number of rows in matrix
            num_cols: Number of columns in matrix
            row_port: Port for row control ('A' or 'B')
            col_port: Port for column control ('A' or 'B')
        """
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.row_port = row_port
        self.col_port = col_port
        
        self.mcp = MCP23S17()
        logger.info(f"Matrix controller initialized: {num_rows}x{num_cols}")

    def press_button(self, row: int, col: int, duration: float = 0.1) -> None:
        """Press a matrix button"""
        if not (0 <= row < self.num_rows and 0 <= col < self.num_cols):
            raise ValueError(f"Invalid matrix position [{row}][{col}]")
        
        self.mcp.pulse_row_column(row, col, self.row_port, self.col_port, duration)

    def press_sequence(self, buttons: List[Tuple[int, int]], 
                      duration: float = 0.1, interval: float = 0.2) -> None:
        """Press a sequence of matrix buttons"""
        self.mcp.matrix_sequence(buttons, self.row_port, self.col_port, 
                                duration, interval)

    def cleanup(self) -> None:
        """Cleanup resources"""
        self.mcp.cleanup()


if __name__ == "__main__":
    # Example usage
    try:
        # Initialize controller
        controller = MatrixController(num_rows=4, num_cols=4, 
                                     row_port='A', col_port='B')
        
        logger.info("Starting matrix controller demonstration")
        
        # Example 1: Press individual button
        logger.info("Example 1: Pressing individual buttons")
        controller.press_button(0, 0, duration=0.1)
        time.sleep(0.5)
        controller.press_button(2, 3, duration=0.1)
        time.sleep(0.5)
        
        # Example 2: Press button sequence
        logger.info("Example 2: Pressing button sequence")
        sequence = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2), (3, 3)]
        controller.press_sequence(sequence, duration=0.1, interval=0.3)
        
        logger.info("Examples completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        controller.cleanup()
