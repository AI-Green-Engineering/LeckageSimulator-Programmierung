from flask import Flask, request
import serial
import time
from datetime import datetime

ser = serial.Serial('/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_ETCRj137C01-if00-port0', 9600)


name = 'main'
app = Flask(name)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == "POST":
        button_value = request.form.get('button')
        print("button value: ", button_value)
        if button_value == "open":
            command = "1a"
            ser.write(command.encode('utf-8')+b"\r\n")
        if button_value == "close":
            command = "1z"
            ser.write(command.encode('utf-8')+b"\r\n")
    return """
    <html>
        <body>
            <h1>Hello World</h1>
            <form method="POST">
                <button id="open" name="button" type="submit" value="open">open</button>
                <button id="close" name="button" type="submit" value="close">close</button>
            </form>
        </body>
        <script>
            console.log("script is running.")
            /*
            let open = document.getElementById('open');
            let close = document.getElementById('close');

            console.log(open);

            open.addEventListener("click", () => console.log("Hallo Welt"));
            */
        </script>
    </html>
    """

if name == 'main':
    app.run(debug=True, host='0.0.0.0')

