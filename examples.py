"""
MCP23S17 Matrix Controller - Usage Examples
Demonstrates various ways to control matrix inputs via MCP23S17
"""

import time
import logging
from mcp23s17_controller import MCP23S17, MatrixController

# Set logging level for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_pin_control():
    """Example 1: Basic individual pin control"""
    logger.info("\n=== Example 1: Basic Pin Control ===")
    
    mcp = MCP23S17(bus=0, device=0, speed_hz=100000)
    
    try:
        # Turn on individual pins
        logger.info("Turning on pins...")
        mcp.set_pin_high('A', 0)
        time.sleep(0.5)
        mcp.set_pin_high('A', 1)
        time.sleep(0.5)
        
        # Turn off pins
        logger.info("Turning off pins...")
        mcp.set_pin_low('A', 0)
        time.sleep(0.5)
        mcp.set_pin_low('A', 1)
        time.sleep(0.5)
        
        # Toggle pins
        logger.info("Toggling pins...")
        for _ in range(3):
            mcp.toggle_pin('B', 0)
            time.sleep(0.3)
    
    finally:
        mcp.cleanup()


def example_pulse_simulation():
    """Example 2: Pulse simulation for button press"""
    logger.info("\n=== Example 2: Pulse Simulation ===")
    
    mcp = MCP23S17(bus=0, device=0, speed_hz=100000)
    
    try:
        # Short pulse (quick button press)
        logger.info("Quick pulse...")
        mcp.pulse_pin('A', 0, duration=0.05)
        time.sleep(1)
        
        # Long pulse
        logger.info("Long pulse...")
        mcp.pulse_pin('A', 1, duration=0.5)
    
    finally:
        mcp.cleanup()


def example_matrix_single_press():
    """Example 3: Single matrix button press"""
    logger.info("\n=== Example 3: Single Matrix Press ===")
    
    controller = MatrixController(num_rows=4, num_cols=4, 
                                 row_port='A', col_port='B')
    
    try:
        # Press button at position [1, 2]
        logger.info("Pressing matrix button [1][2]...")
        controller.press_button(row=1, col=2, duration=0.15)
        time.sleep(0.5)
        
        # Press another button
        logger.info("Pressing matrix button [3][1]...")
        controller.press_button(row=3, col=1, duration=0.15)
    
    finally:
        controller.cleanup()


def example_matrix_sequence():
    """Example 4: Sequence of matrix button presses"""
    logger.info("\n=== Example 4: Matrix Button Sequence ===")
    
    controller = MatrixController(num_rows=4, num_cols=4,
                                 row_port='A', col_port='B')
    
    try:
        # Define a sequence of buttons to press
        # This could represent entering a code or menu sequence
        sequence = [
            (0, 0),  # Top-left
            (0, 3),  # Top-right
            (3, 0),  # Bottom-left
            (3, 3),  # Bottom-right
            (1, 1),  # Center-ish
            (2, 2),  # Another center
        ]
        
        logger.info(f"Executing sequence of {len(sequence)} button presses...")
        controller.press_sequence(sequence, duration=0.1, interval=0.4)
    
    finally:
        controller.cleanup()


def example_port_control():
    """Example 5: Controlling entire port at once"""
    logger.info("\n=== Example 5: Port Control ===")
    
    mcp = MCP23S17(bus=0, device=0, speed_hz=100000)
    
    try:
        # Set entire port to binary pattern
        logger.info("Setting port A to pattern 0b10101010...")
        mcp.set_port('A', 0b10101010)
        time.sleep(1)
        
        logger.info("Setting port A to pattern 0b01010101...")
        mcp.set_port('A', 0b01010101)
        time.sleep(1)
        
        # Turn off all
        logger.info("Turning off all pins...")
        mcp.set_port('A', 0x00)
        mcp.set_port('B', 0x00)
    
    finally:
        mcp.cleanup()


def example_complex_matrix_pattern():
    """Example 6: Complex matrix press pattern"""
    logger.info("\n=== Example 6: Complex Matrix Pattern ===")
    
    controller = MatrixController(num_rows=8, num_cols=8,
                                 row_port='A', col_port='B')
    
    try:
        # Press diagonal pattern
        logger.info("Pressing diagonal pattern...")
        diagonal = [(i, i) for i in range(8)]
        controller.press_sequence(diagonal, duration=0.05, interval=0.2)
        
        time.sleep(1)
        
        # Press anti-diagonal
        logger.info("Pressing anti-diagonal pattern...")
        anti_diagonal = [(i, 7-i) for i in range(8)]
        controller.press_sequence(anti_diagonal, duration=0.05, interval=0.2)
        
        time.sleep(1)
        
        # Press first row then first column
        logger.info("Pressing first row...")
        first_row = [(0, i) for i in range(8)]
        controller.press_sequence(first_row, duration=0.05, interval=0.15)
        
        time.sleep(0.5)
        
        logger.info("Pressing first column...")
        first_col = [(i, 0) for i in range(8)]
        controller.press_sequence(first_col, duration=0.05, interval=0.15)
    
    finally:
        controller.cleanup()


def example_low_level_mcp_operations():
    """Example 7: Low-level MCP23S17 operations"""
    logger.info("\n=== Example 7: Low-level Operations ===")
    
    mcp = MCP23S17(bus=0, device=0, speed_hz=100000)
    
    try:
        # Read port states
        logger.info("Reading port states...")
        port_a_state = mcp.get_port_state('A')
        port_b_state = mcp.get_port_state('B')
        logger.info(f"Port A state: 0x{port_a_state:02X} ({port_a_state:08b})")
        logger.info(f"Port B state: 0x{port_b_state:02X} ({port_b_state:08b})")
        
        # Configure individual pins as input/output
        logger.info("Configuring pins...")
        mcp.configure_pin_mode('A', 7, is_output=True)
        time.sleep(0.2)
        
        # Manipulate specific pins
        logger.info("Setting specific pins...")
        mcp.set_pin_high('A', 5)
        mcp.set_pin_high('A', 6)
        mcp.set_pin_high('A', 7)
        time.sleep(1)
        
        # Read current state
        logger.info("Reading updated state...")
        port_a_state = mcp.get_port_state('A')
        logger.info(f"Port A state: 0x{port_a_state:02X} ({port_a_state:08b})")
        
        # Clear
        mcp.set_port('A', 0x00)
    
    finally:
        mcp.cleanup()


def example_timed_sequence():
    """Example 8: Timed sequence with variable intervals"""
    logger.info("\n=== Example 8: Timed Sequence ===")
    
    controller = MatrixController(num_rows=4, num_cols=4,
                                 row_port='A', col_port='B')
    
    try:
        # Simulate typing a code: 0-0, 1-1, 2-2, 3-3
        code_sequence = [(0, 0), (1, 1), (2, 2), (3, 3)]
        
        logger.info("Entering code sequence...")
        for i, (row, col) in enumerate(code_sequence):
            logger.info(f"Entering digit {i+1}: [{row}][{col}]")
            controller.press_button(row, col, duration=0.1)
            
            if i < len(code_sequence) - 1:
                # Variable delay between presses
                delay = 0.5 + (i * 0.1)
                logger.info(f"Waiting {delay}s before next digit...")
                time.sleep(delay)
    
    finally:
        controller.cleanup()


def main():
    """Run all examples"""
    logger.info("\n" + "="*50)
    logger.info("MCP23S17 Matrix Controller - Usage Examples")
    logger.info("="*50)
    
    examples = [
        ("Basic Pin Control", example_basic_pin_control),
        ("Pulse Simulation", example_pulse_simulation),
        ("Single Matrix Press", example_matrix_single_press),
        ("Matrix Sequence", example_matrix_sequence),
        ("Port Control", example_port_control),
        ("Complex Matrix Pattern", example_complex_matrix_pattern),
        ("Low-level Operations", example_low_level_mcp_operations),
        ("Timed Sequence", example_timed_sequence),
    ]
    
    for idx, (name, func) in enumerate(examples, 1):
        try:
            logger.info(f"\n[{idx}/{len(examples)}] Running: {name}")
            func()
            logger.info(f"✓ {name} completed successfully")
            time.sleep(1)
        except Exception as e:
            logger.error(f"✗ {name} failed: {e}")


if __name__ == "__main__":
    try:
        main()
        logger.info("\n" + "="*50)
        logger.info("All examples completed!")
        logger.info("="*50)
    except KeyboardInterrupt:
        logger.info("\n\nExamples interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
