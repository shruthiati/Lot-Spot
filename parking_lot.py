import evdev
import json
import RPi.GPIO as GPIO
import time
import re

# Set up GPIO mode and pins
GPIO.setmode(GPIO.BCM)
entry_gate_pin = 25  # GREEN Change this to the GPIO pin for the entry gate LED
error_led_pin = 24  # RED Change this to the GPIO pin for the exit gate LED
exit_button_pin = 23  # WHITE Change this to the GPIO pin for the exit button
exit_gate_pin = 16  # BLUE Change this to the GPIO pin for the entry gate LED

# Initialize the LED pins as outputs
GPIO.setup(entry_gate_pin, GPIO.OUT)
GPIO.setup(error_led_pin, GPIO.OUT)
GPIO.setup(exit_gate_pin, GPIO.OUT)

# Set up the exit button pin as an input with pull-up resistor
GPIO.setup(exit_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

lot_num = 1
open_spots_file = f'open_spots_lot{lot_num}'
student_database_file = 'student_database.json'
max_num_spots = 5

# Load student database from a JSON file
with open(student_database_file, 'r') as file:
    student_data = json.load(file)
student_data_str = json.dumps(student_data, indent=2)
print(f"student_data: {student_data_str}")

# Find the device associated with the card reader
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
card_reader = None
for device in devices:
    print(device.path, device.name, device.phys)
    if "HID" in device.name:
        card_reader = device
        break

if card_reader is None:
    print("Card reader not found.")
    exit(1)

# Function to blink error LED for 3 seconds.
# What does it do?
#   For 3 seconds, blink the RED led, 0.5 seconds ON, 0.5 seconds OFF.
def blink_error():
    for i in range(3):
        GPIO.output(error_led_pin, GPIO.HIGH)
        time.sleep(.5)
        GPIO.output(error_led_pin, GPIO.LOW)
        time.sleep(.5)

# Function to wait for card swipe, lookup student ID and update the open spots count
# What does it do?
#   1. Forever loop that waits for card swipe.
#   2. When card is swiped, do some data manipulation to get the ID value from the card data. This is using regular_expressions to find the value.
#   3. Look up if the student ID is in the studentID database read from the JSON file.
#       a. If student ID matches
#           i. Read the current num open spots from open_spots file
#           ii. If more than 0 spots are open, open the gate (turn on GREEN LED), decrement the count and update the open_spots file
#           iii. If 0 spots are open, blink RED LED for 3 seconds
#       b. If student ID does not match, blink RED LEF for 3 seconds.
#   4. Go back to beginning of the look and wait for card swipe. Or keyboard interrupt (Ctrl+c) to exit. 
def wait_for_card_swipe(card_reader):
    card_data = []
    try:
        while True:
            print("Waiting for a card swipe...")
            for event in card_reader.read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    #print(f"key_event: {key_event}")
                    if key_event.keystate == key_event.key_down:
                        key = key_event.keycode
                        if key != 'KEY_ENTER':
                            card_data.append(key.split('KEY_')[1])
                        else:
                            card_number = ''.join(card_data)
                            card_data = []
                            #print(f"Card data: {card_number}")
                            pattern = re.compile(r'EQUAL(.*?)EQUAL')
                            matches = re.findall(pattern, card_number)
                            #print(matches)
                            student_id = int(matches[1][:-2])
                            #print(f"ID: {student_id}")

                            # Check if the card number is in the JSON database file
                            if str(student_id) in student_data["database"]:
                                #print(f'student lots: {student_data["database"][str(student_id)]}')
                                if str(lot_num) in student_data["database"][str(student_id)]:
                                    with open (open_spots_file, 'r') as f:
                                        open_spots = int(f.read().strip())
                                    if open_spots > 0:
                                        # Turn on the entry gate LED
                                        GPIO.output(entry_gate_pin, GPIO.HIGH)
                                        # Decrement open spots count
                                        open_spots -= 1
                                        with open(open_spots_file, "w") as f:
                                            f.write(str(open_spots) + "\n")
                                        # Green LED on for 5 seconds
                                        print(f"Student ID found in database, enough spots available, opening entry gate")
                                        time.sleep(5)  # Wait for 5 seconds
                                        GPIO.output(entry_gate_pin, GPIO.LOW)  # Turn off the entry gate LED
                                    else:
                                        print(f'Student ID found in database, but 0 spots available!')
                                        blink_error()
                                else:
                                    print(f"Student does not have access to this lot!")
                                    blink_error()
                            else:
                                print(f"Student ID not found in database.")
                                blink_error()

                            break

    except KeyboardInterrupt:
        pass

# Function that executes when exit button is pressed.
# What does it do?
#   1. Read the number of open spots from the open_spots file
#   2. If the numer of open spots is less than the max spots in the lot, 
#       a. then increment the counter
#       b. update the open_spots file with the new value
#       c. then open the gate (Turn on BLUE LED for 5 seconds) 
#   3. If all spots are open (max num reached), then do not increment the counter, do nothing.
def exit_button_callback(channel):
    global max_num_spots
    with open (open_spots_file, 'r') as f:
        open_spots = int(f.read().strip())

    if open_spots < max_num_spots:
        open_spots += 1
        print("Exit button pressed, incrementing open spots.")
        with open(open_spots_file, "w") as f:
            f.write(str(open_spots) + "\n")
    else:
        print("Exit button pressed, but max count reached, not incrementing open spots.")
    # Blue LED on for 5 seconds
    GPIO.output(exit_gate_pin, GPIO.HIGH)  # Turn on the LED
    time.sleep(5)  # Wait for 5 seconds
    GPIO.output(exit_gate_pin, GPIO.LOW)   # Turn off the LED

# Add event detection to call exit function anytime button is pressed
GPIO.add_event_detect(exit_button_pin, GPIO.FALLING, callback=exit_button_callback, bouncetime=300)

# Call the card swipe function that will run forever.
wait_for_card_swipe(card_reader)

# Clean up and exit
GPIO.cleanup()
print(f"Exiting...")