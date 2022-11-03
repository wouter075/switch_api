import os
import time
from datetime import datetime

import serial
import sqlite3

from serial import SerialException

# setup
PORT_NAME = b'Gi1/0'
SERIAL_PORT = "COM3"
SERIAL_BAUDRATE = 9600
SERIAL_PARITY = serial.PARITY_NONE
SERIAL_STOPBITS = serial.STOPBITS_ONE
SERIAL_BYTESIZE = serial.EIGHTBITS

# variables
DEBUG = os.environ.get('DEBUG', "False") == "True"
sqliteConnection = ''
cursor = ''

try:
    sqliteConnection = sqlite3.connect('sw.db')
    cursor = sqliteConnection.cursor()
    if DEBUG:
        print("Database created and Successfully Connected to SQLite")

    # example of the database
    # q1 = '''CREATE TABLE sw_data (
    # id INTEGER PRIMARY KEY,
    # port TEXT,
    # send INT,
    # receive INT,
    # timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    # );'''
    # cursor.execute(q1)
    # sqliteConnection.commit()
    # cursor.close()

except sqlite3.Error as error:
    if DEBUG:
        print("Error while connecting to sqlite", error)
    exit(1)

while True:
    now = datetime.now()
    ct = now.strftime("%H:%M:%S")

    # configure the serial connection
    ser = serial.Serial()

    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUDRATE,
            parity=SERIAL_PARITY,
            stopbits=SERIAL_STOPBITS,
            bytesize=SERIAL_BYTESIZE,
        )
    except SerialException:
        print(f'Port: {SERIAL_PORT} already in use')

    # does it work?
    if ser.isOpen():
        # flush any previous data
        try:
            ser.flush()

            if DEBUG:
                print("Connection open")
            # disable --More--
            if DEBUG:
                print("Setting terminal length to 0")
            ser.write(b'terminal length 0\r\n')

            # get utilization
            if DEBUG:
                print("Request utilization")
            ser.write(b'sh controllers utilization\r\n')
            out = ''

            while True:
                # read lines
                out = ser.readline()
                if DEBUG:
                    print(out)

                if out.startswith(PORT_NAME):
                    # b'Gi1/0/52   \t   0\t\t\t0\r\n'
                    swPort, p2 = out.split(b'   \t   ')
                    swReceive, swSend = p2.split(b'\t\t\t')
                    swPort = swPort.decode()
                    swSend = swSend.replace(b'\r\n', b'').decode()
                    swReceive = swReceive.decode()
                    # if DEBUG:
                    print(f'[{ct}] {swPort}:\t {swReceive}% / {swSend}%')

                    # update database:
                    v = (swPort, swSend, swReceive)
                    q2 = f'''INSERT INTO sw_data (port, send, receive) VALUES (?, ?, ?)'''
                    cursor.execute(q2, v)
                    sqliteConnection.commit()

                # exit when all data is received
                if b'Stack Ring Percentage' in out:
                    ser.close()
                    break
            time.sleep(30)

        except SerialException as serialError:
            print(f"[Serial] Something went wrong: {serialError}")
        except sqliteConnection.Error as sqlError:
            print(f"[SQLLite] Something went wrong: {sqlError}")
        finally:
            # close connections
            ser.close()
            cursor.close()
            sqliteConnection.close()
            break


if sqliteConnection:
    cursor.close()
    sqliteConnection.close()
