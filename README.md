The Lot Spot 

Description: 
The purpose of this project is to count the number of spots open in a parking garage in Texas State University. 
A raspberryPi paired with a card reader is able to permit some students with access into the garage, while it 
shows an error to those who are not allowed in the garage. A webpage will keep a current count of the number
of spots available for the ease of students trying to find parking in the busy university. 

Installation:
The following items are necessary to run this project:
-raspberryPi
-project board
-power cable
-HDMI cable
-monitor
-keyboard, USB
-mouse, USB
-indicator lights
-jump wires
-card reader, USB
-ID card

The raspberryPi is set up by connecting it to power, and controlled using a mouse, keyboard, and a 
monitor. 

The project board contains the indicator lights, an exit button, and jump wires to complete the circuit. 
(the specific pin and light connections are listed in the parking_lot.py file. 

Files created and used: 
-index.html file contains the html code that projects the counters onto the webpage. 
-open_spots_lot1 file contains the number of open spots defaulted to project onto the webpage before 
running the code
-parking_lot.py file contains the forever loop that runs as the cards are swiped, and the lights turn on
-parkinggarage.jpg contains the background image for the webpage.
-student_database.json contains the list of IDs that are permitted into the garage. 
-styles.css file contains the styling used while creating the front end webpage design
-texasstatelogo.jpg is an image of the Texas State logo for the webpage.

In order to run the code, the following command has to be run. 
Command to start the script on raspberryPi:
```
/usr/bin/python3 /home/pi/parking_lot/parking_lot.py
```
Press Ctrl+C to end the script. It will be in an endless loop untill interrupted


Features: 

When running the code, there are 3 possible outcomes:

1. If a card is swiped, and that student has access to the garage, the green light will turn on. 
This indicates that the garage entry gate has opened, while the count on the webpage will decrement
to indicate there is one less spot open. 

2. If a card is swiped, and that student does not have access to the garage or if there are no spots 
available, the red light will turn on. This indicates that the garage entry gate is not going to open. 
The count on the webpage will not change. 

3. If the button is pressed at the exit gate, the blue light will turn on. This indicates that the 
garage exit gate has opened, while the count on the webpage will increment to indicate there is one 
more spot now open. 

Happy parking!

Authors:
Shruthi Ati
Lois Han
Meredith Huerta
Courtney Wehner
