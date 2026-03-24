import serial
import time
from datetime import datetime

ser = serial.Serial('/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_ETCRj137C01-if00-port0', 9600)

stepCounter = -1
START_VALUE = 0
FULLY_OPEN = 1000
STEP_SIZE = 10
TIME_TO_WAIT_IN_SECONDS = 20

def gotoReferencePoint():
    """
    send 'R'
    """
    global stepCounter
    stepCounter = START_VALUE

def gotoEndPoint():
    """
    send '<number>a'
    Note: Prototype should no be open at this stage
    stepCounter += <number>
    """

def loopAndWait():
    """
    send '1a' every 10 seconds until stepCounter >= Start
    """
    global stepCounter
    while stepCounter < FULLY_OPEN:
        command = str(STEP_SIZE) + "a"
        ser.write(command.encode('utf-8')+b"\r\n")
        stepCounter += STEP_SIZE
        print(stepCounter)
        time.sleep(TIME_TO_WAIT_IN_SECONDS)

def __main__():
    print("start time", datetime.now())
    gotoReferencePoint()
    gotoEndPoint()
    loopAndWait()
    print("end time", datetime.now())

__main__()
