#!/usr/bin/env python3
"""
3x4 Matrix Controller Example
Keypad layout:
  1   2   3   CALL
  4   5   6   0
  7   8   9   CLR

Hardware Configuration:
- Rows (3): Port A pins 0-2 (GPIO A0, A1, A2)
- Columns (4): Port B pins 0-3 (GPIO B0, B1, B2, B3)

Matrix mapping:
Button Position -> (Row, Column)
  1 -> (0, 0)    2 -> (0, 1)    3 -> (0, 2)  CALL -> (0, 3)
  4 -> (1, 0)    5 -> (1, 1)    6 -> (1, 2)    0 -> (1, 3)
  7 -> (2, 0)    8 -> (2, 1)    9 -> (2, 2)  CLR -> (2, 3)
"""

import sys
import time
import logging
from typing import Dict, List, Tuple

# Add parent directory to path to import mcp23s17_controller
sys.path.insert(0, '/home/pi/mcp23s17_matrix_controller')

from mcp23s17_controller import MatrixController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Keypad3x4:
    """3x4 Keypad controller with button name mapping"""
    
    # Button mapping: button_name -> (row, col)
    BUTTON_MAP = {
        '1':    (0, 0),
        '2':    (0, 1),
        '3':    (0, 2),
        'CALL': (0, 3),
        '4':    (1, 0),
        '5':    (1, 1),
        '6':    (1, 2),
        '0':    (1, 3),
        '7':    (2, 0),
        '8':    (2, 1),
        '9':    (2, 2),
        'CLR':  (2, 3),
    }
    
    # Reverse mapping: (row, col) -> button_name
    POSITION_MAP = {v: k for k, v in BUTTON_MAP.items()}
    
    def __init__(self, row_port: str = 'A', col_port: str = 'B'):
        """
        Initialize 3x4 keypad controller
        
        Args:
            row_port: Port for row control (default 'A')
            col_port: Port for column control (default 'B')
        """
        self.controller = MatrixController(
            num_rows=3,
            num_cols=4,
            row_port=row_port,
            col_port=col_port
        )
        logger.info("3x4 Keypad initialized")
    
    def press_button(self, button_name: str, duration: float = 0.1) -> None:
        """
        Press a button by name
        
        Args:
            button_name: Button identifier ('1'-'9', '0', 'CALL', 'CLR')
            duration: Pulse duration in seconds
        """
        if button_name not in self.BUTTON_MAP:
            raise ValueError(f"Invalid button: {button_name}")
        
        row, col = self.BUTTON_MAP[button_name]
        logger.info(f"Pressing button '{button_name}' at [{row}][{col}]")
        self.controller.press_button(row, col, duration)
    
    def press_sequence(self, button_sequence: str, 
                      duration: float = 0.1, interval: float = 0.2) -> None:
        """
        Press a sequence of buttons
        
        Args:
            button_sequence: String of button names (e.g., "12345" or "1 2 3 CALL")
            duration: Pulse duration per button
            interval: Time between button presses
        """
        # Parse button sequence (handles both "12345" and "1 2 3 CALL" formats)
        buttons = button_sequence.replace(' ', '').split()
        if len(buttons) == 1:
            # If no spaces, treat as individual characters
            buttons = list(button_sequence)
        
        logger.info(f"Pressing sequence: {' '.join(buttons)}")
        
        coordinates = []
        for button in buttons:
            button = button.strip()
            if not button:
                continue
            if button not in self.BUTTON_MAP:
                logger.warning(f"Skipping invalid button: {button}")
                continue
            coordinates.append(self.BUTTON_MAP[button])
        
        if coordinates:
            self.controller.press_sequence(coordinates, duration, interval)
    
    def get_button_layout(self) -> str:
        """Return ASCII representation of keypad layout"""
        return """
3x4 Keypad Layout:
┌─────┬─────┬─────┬──────┐
│  1  │  2  │  3  │ CALL │  Row 0
├─────┼─────┼─────┼──────┤
│  4  │  5  │  6  │  0   │  Row 1
├─────┼─────┼─────┼──────┤
│  7  │  8  │  9  │ CLR  │  Row 2
└─────┴─────┴─────┴──────┘
  Col Col Col  Col
   0   1   2    3
"""
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        self.controller.cleanup()
        logger.info("Keypad cleanup complete")


def example_1_single_buttons():
    """Example 1: Press individual buttons"""
    logger.info("=" * 60)
    logger.info("Example 1: Press Individual Buttons")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        print(keypad.get_button_layout())
        
        # Press each button
        buttons_to_press = ['1', '5', '9', 'CALL', '0', 'CLR']
        
        for button in buttons_to_press:
            logger.info(f"Pressing button: {button}")
            keypad.press_button(button, duration=0.15)
            time.sleep(0.3)
        
        logger.info("Example 1 completed")
        keypad.cleanup()
        
    except Exception as e:
        logger.error(f"Example 1 failed: {e}")


def example_2_phone_sequence():
    """Example 2: Simulate dialing a phone number"""
    logger.info("=" * 60)
    logger.info("Example 2: Dial Phone Number (123-456-7890)")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        
        # Simulate dialing: 123-456-7890
        phone_number = "123 456 7890"
        logger.info(f"Dialing: {phone_number}")
        
        keypad.press_sequence(phone_number, duration=0.1, interval=0.25)
        
        logger.info("Phone number dialed")
        keypad.cleanup()
        
    except Exception as e:
        logger.error(f"Example 2 failed: {e}")


def example_3_calculator_sequence():
    """Example 3: Calculator input sequence"""
    logger.info("=" * 60)
    logger.info("Example 3: Calculator Sequence (5 + 3 =)")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        
        # Press: 5, then wait, then 3, then CALL (for =)
        logger.info("Entering: 5 + 3 =")
        
        keypad.press_button('5', duration=0.1)
        time.sleep(0.5)
        
        keypad.press_button('3', duration=0.1)
        time.sleep(0.5)
        
        keypad.press_button('CALL', duration=0.1)  # Simulate = button
        
        logger.info("Calculator sequence completed")
        keypad.cleanup()
        
    except Exception as e:
        logger.error(f"Example 3 failed: {e}")


def example_4_clear_pattern():
    """Example 4: Enter and clear pattern"""
    logger.info("=" * 60)
    logger.info("Example 4: Enter Pattern Then Clear")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        
        # Enter: 1, 2, 3, 4, 5, then CALL to submit, then CLR to clear
        pattern = "12345"
        logger.info(f"Entering pattern: {pattern}")
        
        keypad.press_sequence(pattern, duration=0.1, interval=0.2)
        time.sleep(0.5)
        
        logger.info("Pressing CALL to submit")
        keypad.press_button('CALL', duration=0.1)
        time.sleep(0.5)
        
        logger.info("Pressing CLR to clear")
        keypad.press_button('CLR', duration=0.1)
        
        logger.info("Clear pattern completed")
        keypad.cleanup()
        
    except Exception as e:
        logger.error(f"Example 4 failed: {e}")


def example_5_grid_scan():
    """Example 5: Scan all buttons in grid order"""
    logger.info("=" * 60)
    logger.info("Example 5: Scan All Buttons (Row by Row)")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        
        logger.info("Scanning all buttons in grid order...")
        
        for row in range(3):
            for col in range(4):
                button_name = Keypad3x4.POSITION_MAP[(row, col)]
                logger.info(f"Pressing [{row}][{col}] -> {button_name}")
                keypad.press_button(button_name, duration=0.1)
                time.sleep(0.2)
        
        logger.info("Grid scan completed")
        keypad.cleanup()
        
    except Exception as e:
        logger.error(f"Example 5 failed: {e}")


def example_6_numeric_entry():
    """Example 6: Enter all numeric digits"""
    logger.info("=" * 60)
    logger.info("Example 6: Enter All Digits (0-9)")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        
        # Enter digits in order: 1, 2, 3, 4, 5, 6, 7, 8, 9, 0
        digit_sequence = "1234567890"
        logger.info(f"Entering all digits: {digit_sequence}")
        
        keypad.press_sequence(digit_sequence, duration=0.1, interval=0.15)
        
        logger.info("Numeric entry completed")
        keypad.cleanup()
        
    except Exception as e:
        logger.error(f"Example 6 failed: {e}")


def example_7_menu_navigation():
    """Example 7: Simulate menu navigation with special buttons"""
    logger.info("=" * 60)
    logger.info("Example 7: Menu Navigation (CALL, CLR, Digits)")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        
        # Navigate: Press 2 (down), 3 (option), CALL (select), CLR (back)
        logger.info("Menu: Down (2), Option (3), Select (CALL), Back (CLR)")
        
        logger.info("Moving down...")
        keypad.press_button('2', duration=0.1)
        time.sleep(0.3)
        
        logger.info("Selecting option...")
        keypad.press_button('3', duration=0.1)
        time.sleep(0.3)
        
        logger.info("Confirming selection...")
        keypad.press_button('CALL', duration=0.1)
        time.sleep(0.3)
        
        logger.info("Going back...")
        keypad.press_button('CLR', duration=0.1)
        
        logger.info("Menu navigation completed")
        keypad.cleanup()
        
    except Exception as e:
        logger.error(f"Example 7 failed: {e}")


def example_8_custom_sequence():
    """Example 8: Custom multi-step sequence"""
    logger.info("=" * 60)
    logger.info("Example 8: Complex Multi-Step Sequence")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        
        # Step 1: Enter code
        logger.info("Step 1: Entering security code (5555)")
        keypad.press_sequence("5555", duration=0.1, interval=0.2)
        time.sleep(0.5)
        
        # Step 2: Confirm
        logger.info("Step 2: Pressing CALL to confirm")
        keypad.press_button('CALL', duration=0.1)
        time.sleep(0.5)
        
        # Step 3: Enter amount
        logger.info("Step 3: Entering amount (100)")
        keypad.press_sequence("100", duration=0.1, interval=0.2)
        time.sleep(0.5)
        
        # Step 4: Finalize
        logger.info("Step 4: Pressing CALL to finalize")
        keypad.press_button('CALL', duration=0.1)
        
        logger.info("Complex sequence completed")
        keypad.cleanup()
        
    except Exception as e:
        logger.error(f"Example 8 failed: {e}")


def example_9_quick_test():
    """Example 9: Quick test - Press button 1 (0,0), then CALL"""
    logger.info("=" * 60)
    logger.info("Example 9: Quick Test - Button 1 + CALL")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        
        logger.info("Pressing button 1 (row 0, col 0)")
        keypad.press_button('1', duration=0.1)
        time.sleep(0.3)
        
        logger.info("Pressing CALL button")
        keypad.press_button('CALL', duration=0.1)
        
        logger.info("Quick test completed")
        keypad.cleanup()
        
    except Exception as e:
        logger.error(f"Example 9 failed: {e}")


def test_number_input():
    """Test function: Input a number and send button strokes"""
    logger.info("=" * 60)
    logger.info("Number Input Test (0-999)")
    logger.info("=" * 60)
    
    try:
        keypad = Keypad3x4()
        
        while True:
            print("\n" + "-" * 60)
            user_input = input("Enter a number (0-999) or 'q' to quit: ").strip()
            
            if user_input.lower() == 'q':
                logger.info("Exiting number input test")
                break
            
            # Validate input
            try:
                number = int(user_input)
                if not 0 <= number <= 999:
                    print(f"ERROR: Number must be between 0 and 999 (got {number})")
                    continue
            except ValueError:
                print(f"ERROR: Invalid input '{user_input}'. Please enter a number.")
                continue
            
            # Convert number to string with leading zeros if needed
            # e.g., 5 -> "005", 42 -> "042", 123 -> "123"
            number_str = str(number).zfill(3)
            
            logger.info(f"Sending number: {number} (buttons: {number_str} + CALL)")
            print(f"Pressing buttons: {number_str[0]} -> {number_str[1]} -> {number_str[2]} -> CALL")
            
            # Press each digit
            for digit in number_str:
                keypad.press_button(digit, duration=0.1)
                time.sleep(0.2)
            
            # Press CALL button
            logger.info("Pressing CALL button")
            keypad.press_button('CALL', duration=0.1)
            
            print(f"✓ Sequence complete for number {number}")
        
        keypad.cleanup()
        logger.info("Number input test ended")
        
    except Exception as e:
        logger.error(f"Number input test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all examples"""
    import argparse
    
    parser = argparse.ArgumentParser(description='3x4 Keypad Controller Examples')
    parser.add_argument('example', type=int, nargs='?', default=0,
                       help='Example number (1-8), 9 for number test, or 0 for menu (default: 0)')
    
    args = parser.parse_args()
    
    examples = {
        1: example_1_single_buttons,
        2: example_2_phone_sequence,
        3: example_3_calculator_sequence,
        4: example_4_clear_pattern,
        5: example_5_grid_scan,
        6: example_6_numeric_entry,
        7: example_7_menu_navigation,
        8: example_8_custom_sequence,
        9: example_9_quick_test,
        10: test_number_input,
    }
    
    if args.example == 0:
        # Show menu
        print("\n" + "=" * 60)
        print("3x4 Keypad Controller - Example Menu")
        print("=" * 60)
        print("Available examples:")
        print("  1 - Press individual buttons")
        print("  2 - Dial phone number (123-456-7890)")
        print("  3 - Calculator sequence (5 + 3 =)")
        print("  4 - Enter and clear pattern")
        print("  5 - Scan all buttons (grid order)")
        print("  6 - Enter all digits (0-9)")
        print("  7 - Menu navigation")
        print("  8 - Complex multi-step sequence")
        print("  9 - QUICK TEST: Button 1 (0,0) + CALL")
        print(" 10 - TEST: Interactive number input (0-999) + CALL")
        print("\nUsage: python example_3x4_matrix.py [example_number]")
        print("=" * 60 + "\n")
    elif args.example in examples:
        examples[args.example]()
    else:
        print(f"Invalid example number: {args.example}")
        print("Valid examples: 1-10, or 0 for menu")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
