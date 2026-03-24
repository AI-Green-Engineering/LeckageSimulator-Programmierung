import serial

ser = serial.Serial('/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_ETCRj137C01-if00-port0', 9600)

ser.flush()

ser.write(b"S")

while True:
    line = ser.readline().decode('utf-8').rstrip()
    print(line)


ser.close()
