from freewili import FreeWili
from freewili.framing import ResponseFrame
from freewili.types import EventDataType, EventType, IRData
import time
import random

current_light = -1

keyboard_interrupt_requested = False

color_to_ir = {"White" : bytes([0xBE, 0xEF, 00, 0xFA]),
               "Yellow" : bytes([0xBE, 0xEF, 00, 0xFB]), 
               "Green" : bytes([0xBE, 0xEF, 00, 0xEC]), 
               "Blue" : bytes([0xBE, 0xEF, 00, 0xFD]), 
               "Red" : bytes([0xBE, 0xEF, 00, 0xFE])}

ir_to_color = {bytes([0xBE, 0xEF, 00, 0xFA]) : "White",
               bytes([0xBE, 0xEF, 00, 0xFB]) : "Yellow", 
               bytes([0xBE, 0xEF, 00, 0xEC]) : "Green", 
               bytes([0xBE, 0xEF, 00, 0xFD]) : "Blue", 
               bytes([0xBE, 0xEF, 00, 0xFE]) : "Red"}

countdown_timer_ms = 0
time_before_death_ms = 10000

def event_callback(event_type: EventType, response_frame: ResponseFrame, event_data: EventDataType) -> None:
    """Callback function to handle events from FreeWili."""
    if isinstance(event_data, IRData):
        print(f"IR RX {len(event_data.value)}: {event_data.value!r}")
        reset(event_data)


def reset(x : IRData):

    global current_light

    if x.value == list(ir_to_color.keys())[current_light]:

        device.set_board_leds(current_light, 0, 0, 0)
        countdown_timer_ms = 0

        current_light = random.randint(0, 4)
        device.set_board_leds(current_light, 10, 10, 4).expect("Failed to set LED")


def game_over():
    keyboard_interrupt_requested = True

# find a FreeWili device and open it
device = FreeWili.find_first().expect("Failed to find a FreeWili")
device.open().expect("Failed to open")

for i in range(7):
    device.set_board_leds(i, 0, 0, 0)




# Read the buttons and print on change
print("Reading buttons...")
last_button_read = device.read_all_buttons().expect("Failed to read buttons")


device.set_event_callback(event_callback)
device.enable_ir_events(True).expect("Failure to enable IR events.")

current_light = random.randint(0, 4)
device.set_board_leds(current_light, 10, 10, 4).expect("Failed to set LED")


while not keyboard_interrupt_requested:
    try:

        if (countdown_timer_ms > time_before_death_ms):
            keyboard_interrupt_requested = True

        device.process_events()
        # Read the buttons
        buttons = device.read_all_buttons().expect("Failed to read buttons")
        for button_color, button_state in buttons.items():
            # Check if the button state has changed
            last_button_state = last_button_read[button_color]
            if last_button_state == button_state:
                continue
            # Print the button change

            msg = "Pressed \N{WHITE HEAVY CHECK MARK}"

            if button_state == 1:
                device.send_ir(color_to_ir[button_color.name]).expect("Failed to send IR command")

            print(f"{button_color.name} {msg}")
        # Save the button state for the next loop
        last_button_read = buttons
        time.sleep(0.001)
    except KeyboardInterrupt:
        device.enable_ir_events(False).expect("Failed to disable IR events")
        keyboard_interrupt_requested = True


device.close()
