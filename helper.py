import time
from datetime import datetime

import serial
import sqlite3

DEBUG = False
sqliteConnection = ''
cursor = ''

try:
    sqliteConnection = sqlite3.connect('sw.db')
    cursor = sqliteConnection.cursor()
    if DEBUG:
        print("Database created and Successfully Connected to SQLite")

    # q1 = '''CREATE TABLE sw_data (
    # id INTEGER PRIMARY KEY,
    # port TEXT,
    # send INT,
    # receive INT,
    # timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    # );'''
    # cursor.execute(q1)
    # sqliteConnection.commit()

    # sqlite_select_Query = "select sqlite_version();"
    # cursor.execute(sqlite_select_Query)
    # record = cursor.fetchall()
    # print("SQLite Database Version is: ", record)
    # cursor.close()

except sqlite3.Error as error:
    if DEBUG:
        print("Error while connecting to sqlite", error)
    exit(1)

while True:
    now = datetime.now()

    ct = now.strftime("%H:%M:%S")
    # print("Current Time =", current_time)

    # configure the serial connection
    ser = serial.Serial(
        port='COM3',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
    )
    ser.flush()

    # does it work?
    if ser.isOpen():
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
        # ser.flush()

        while True:
            # read lines
            out = ser.readline()
            if DEBUG:
                print(out)

            if out.startswith(b'Gi1/0'):
                # b'Gi1/0/52   \t   0\t\t\t0\r\n'
                swPort, p2 = out.split(b'   \t   ')
                swReceive, swSend = p2.split(b'\t\t\t')
                swPort = swPort.decode()
                swSend = swSend.replace(b'\r\n', b'').decode()
                swReceive = swReceive.decode()
                # if DEBUG:
                print(f'[{ct}] {swPort}:\t {swReceive}% / {swSend}%')

                # update database:
                q2 = f'''INSERT INTO sw_data (port, send, receive) VALUES ("{swPort}", {swSend}, {swReceive})'''
                cursor.execute(q2)
                sqliteConnection.commit()

            # exit when all data is received
            if b'Stack Ring Percentage' in out:
                ser.close()
                break
        time.sleep(30)

if sqliteConnection:
    cursor.close()
    sqliteConnection.close()




