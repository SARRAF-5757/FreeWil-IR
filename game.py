"""
- Red button (rightmost) switches between SEND and RECEIVE modes
- SEND mode: Press any button to send a random light to other device
- RECEIVE mode: Wait for other device's signal and respond with matching button
"""

from freewili import FreeWili
from freewili.framing import ResponseFrame
from freewili.types import EventDataType, EventType, IRData
import time
import random

# IR signal mappings based on documentation pattern
# Using sequential pattern: 0xBE, 0xEF, 0x00, [COMMAND_BYTE]
color_to_ir = {
    "White": bytes([0xBE, 0xEF, 0x00, 0xF0]),
    "Yellow": bytes([0xBE, 0xEF, 0x00, 0xF1]), 
    "Green": bytes([0xBE, 0xEF, 0x00, 0xF2]), 
    "Blue": bytes([0xBE, 0xEF, 0x00, 0xF3]), 
    "Red": bytes([0xBE, 0xEF, 0x00, 0xF4])
}

ir_to_color = {
    bytes([0xBE, 0xEF, 0x00, 0xF0]): "White",
    bytes([0xBE, 0xEF, 0x00, 0xF1]): "Yellow", 
    bytes([0xBE, 0xEF, 0x00, 0xF2]): "Green", 
    bytes([0xBE, 0xEF, 0x00, 0xF3]): "Blue", 
    bytes([0xBE, 0xEF, 0x00, 0xF4]): "Red"
}

# Game state
current_mode = "RECEIVE"  # Start in receive mode
current_light = None
device = None

def event_callback(event_type: EventType, response_frame: ResponseFrame, event_data: EventDataType) -> None:
    """Handle received IR signals."""
    if isinstance(event_data, IRData):
        print(f"IR RX: {event_data.value!r}")
        handle_received_signal(event_data)

def handle_received_signal(ir_data: IRData):
    """Process received IR signal and light up corresponding LED."""
    global current_light
    global current_mode
    if (current_mode == "SEND"):
        return
    
        

    received_bytes = bytes(ir_data.value)

    if received_bytes in ir_to_color:
        color = ir_to_color[received_bytes]
        print(f"Received {color} signal!")

        if (ir_data.value == list(ir_to_color.keys())[current_light]):
            device.set_board_leds(current_light, 0, 0, 0).expect("Failed to set LED")

            current_light = random.randint(0, 3)
            device.set_board_leds(current_light, 10, 10, 4).expect("Failed to set LED")
        
    else:
        print(f"Unknown signal received: {ir_data.value!r}")

def clear_all_leds():
    """Turn off all LEDs."""
    for i in range(7):
        device.set_board_leds(i, 0, 0, 0)

def main():
    global device, current_mode
    
    print("FreeWili Two-Mode IR Game")
    print("=" * 30)
    print("Red button (rightmost): Switch between SEND/RECEIVE modes")
    print("SEND mode: Press any button to send corresponding light")
    print("RECEIVE mode: Wait for other device's signal")
    print("Press Ctrl+C to exit")
    print("=" * 30)


    # Initialize device
    device = FreeWili.find_first().expect("Failed to find FreeWili")
    device.open().expect("Failed to open")
    
    # Clear all LEDs
    clear_all_leds()
    
    # Set up IR event handling
    device.set_event_callback(event_callback)
    device.enable_ir_events(True).expect("Failed to enable IR events")
    
    # Read initial button state
    last_button_read = device.read_all_buttons().expect("Failed to read buttons")

    #Light initial button
    current_light = random.randint(0, 3)
    device.set_board_leds(current_light, 10, 10, 4)
    
    print(f"Starting in {current_mode} mode")
    
    try:
        while True:
            # Process IR events
            device.process_events()
            
            # Read buttons
            buttons = device.read_all_buttons().expect("Failed to read buttons")
            
            for button_color, button_state in buttons.items():
                last_button_state = last_button_read[button_color]
                
                # Check for button press (state change from 0 to 1)
                if last_button_state == 0 and button_state == 1:
                    print(f"{button_color.name} button pressed")
                    
                    if button_color.name == "Red":
                        # Red button switches mode
                        if current_mode == "RECEIVE":
                            current_mode = "SEND"

                            for i in range(4, 7):
                                device.set_board_leds(i, 10, 4, 4).expect("Failed to set LED")
                            print("Switched to SEND mode")
                            print("Press any button to send the corresponding light to other device")
                        else:
                            current_mode = "RECEIVE"


                            for i in range(4, 7):
                                device.set_board_leds(i, 0, 0, 0).expect("Failed to set LED")
                            print("Switched to RECEIVE mode")
                            print("Waiting for other device's signal...")

                    elif current_mode == "SEND":

                        device.send_ir(color_to_ir[button_color.name]).expect("Failed to send IR command")
            
            # Update button state
            last_button_read = buttons
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
        device.enable_ir_events(False).expect("Failed to disable IR events")
        device.close()

if __name__ == "__main__":
    main()