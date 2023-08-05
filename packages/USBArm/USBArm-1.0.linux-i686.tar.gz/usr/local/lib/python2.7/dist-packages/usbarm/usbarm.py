#!/usr/bin/env python
# USB Robotic Arm Control Module for Python 2.7

'''
A Python module that allows control of a USB arm with a Unix PC.
PyUSB must be installed for this module to work.
To initialise a connection to the arm, use the command 'usbarm.connect()'.
To send instructions to the arm, use the command 'usbarm.ctrl(duration, command)'.
The duration sets how long the command runs for, and the command tells the arm what to do.

Here are the commands you can use:
usbarm.rotate_ccw
usbarm.rotate_cw
usbarm.shoulder_up
usbarm.shoulder_down
usbarm.elbow_up
usbarm.elbow_down
usbarm.wrist_up
usbarm.wrist_down
usbarm.grip_open
usbarm.grip_close
usbarm.light_on
'''

# Define controls to move arm
rotate_ccw = [0,1,0] # Rotate base counter-clockwise
rotate_cw = [0,2,0] # Rotate base clockwise
shoulder_up = [64,0,0] # Shoulder up
shoulder_down = [128,0,0] # Shoulder down
elbow_up = [16,0,0] # Elbow up
elbow_down = [32,0,0] # Elbow down
wrist_up = [4,0,0] # Wrist up
wrist_down = [8,0,0] # Wrist down
grip_open = [2,0,0] # Open grip
grip_close = [1,0,0] # Close grip
light_on = [0,0,1] # Light on

# Define a procedure to connect to the arm via USB
def connect():
    '''
    Connect to the USB arm.
    '''
    global usb_arm
    # Attempt to import the USB and time libraries into Python
    try:
        from time import sleep
    except:
        raise Exception("Time library not found")
    try:
        import usb.core, usb.util
    except:
        raise Exception("USB library not found")
    usb_arm = usb.core.find(idVendor=0x1267, idProduct=0x000)
    # Check if the arm is detected and warn if not
    if usb_arm == None:
        raise Exception("Robotic arm not found")
    else:
        return True

# Define a procedure to transfer commands via USB to the arm
def ctrl(duration, command):
    '''
    Send a command to the USB arm.
    '''
    if usb_arm == None:
        raise Exception("Robotic arm not connected")
    # Start the movement
    usb_arm.ctrl_transfer(0x40,6,0x100,0,command,1000)
    # Stop the movement after waiting a specified duration
    sleep(duration)
    usb_arm.ctrl_transfer(0x40,6,0x100,0,[0,0,0],1000)
    return True

if __name__ == "__main__":
    raise Exception("Cannot run standalone - use 'import usbarm' to utlise this module")
    exit()
