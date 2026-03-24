import serial

ser = serial.Serial('/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_ETCRj137C01-if00-port0', 9600)

while True:
    command = input("Geben Sie einen Befehl ein (q = Quit): ")
    if command == 'q':
        break;
    ser.write(command.encode('utf-8')+b"\r\n")


ser.close()
