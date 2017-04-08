import time
import subprocess
import sys
from Hover_library2 import Hover

hover = Hover(address=0x42, ts=23, reset=24)
sys.stdout.flush()

try:
    while True:

        # Check if hover is ready to send gesture or touch events
        if (hover.getStatus() == 0):

            # Read i2c data and print the type of gesture or touch event
            event = hover.getEvent()

            if event is not None:
                # print (event)
                # This line can be commented out if you don't want to see the
                # event in text format
                try:
                    direction = hover.getEventString(event)
                except:
                    #print ("Invalid input recieved from hover, ignoring.")
                    direction = ''

                print (direction)
                sys.stdout.flush()


            # Release the ts pin until Hover is ready to send the next event
            hover.setRelease()
        time.sleep(0.01)  # sleep for 10ms

except KeyboardInterrupt:
    print ("Exiting...")
    hover.end()
# except:
#     print "Something has gone wrong...:("
#     hover.end()
