import serial
import re

ser = serial.Serial('/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_ETCRj137C01-if00-port0', 9600)

stepCounter = -1
MAX_CHANGE = 500

def checkCommand(command):
    if command == 'q':
        return True
    if command == 'R':
        return True
    if command == '?':
        return True
    if 'a' in command:
        pattern = r"[0-9]+a$"
        if re.match(pattern, command):
            return True
        else:
            return False
    if 'z' in command:
        pattern = r"[0-9]+z$"
        if re.match(pattern, command):
            return True
        else:
            return False
    return False

while True:
    command = input(f"Geben Sie einen Befehl ein (q: Quit, ?: Help, stepCounter = {stepCounter}): ")
    if checkCommand(command):
        if command == 'q':
            break;
        if command == '?':
            print("a: auf, z. B. '10a' für 10 Schritte auf")
            print("z: zu,  z. B. '10z' für 10 Schritte zu")
            print("R: Referenzpunkt --> sets stepCounter to 0")
        if 'a' in command:
            pattern =r"[0-9]+"
            steps = int(re.search(pattern, command).group())
            if (steps > MAX_CHANGE):
                print("Die Anzahl der Schritte ist zu hoch.")
                continue
            stepCounter += steps
        if 'z' in command:
            pattern =r"[0-9]+"
            steps = int(re.search(pattern, command).group())
            if (steps > MAX_CHANGE):
                print("Die Anzahl der Schritte ist zu hoch.")
                continue
            stepCounter -= steps
        if command == 'R':
            stepCounter = 0
        ser.write(command.encode('utf-8')+b"\r\n")
    else:
        print("Der Befehl wurde nicht erkannt.")

    

ser.close()
