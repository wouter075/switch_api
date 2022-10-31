from flask import Flask
import serial
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/login/')
def login():
    # ser = serial.Serial('COM3', 38400, timeout=0, parity = serial.PARITY_EVEN, rtscts = 1)
    ser = serial.Serial('COM3')
    s = ser.read()
    
    return s


if __name__ == '__main__':
    app.run()
