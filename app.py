from flask import Flask, jsonify
import sqlite3
PORT_NAME = 'Gi1/0'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Sorry, no endpoints here.'


@app.route('/ports')
def ports():
    al = []
    try:
        sqlite_connection = sqlite3.connect('sw.db')
        cursor = sqlite_connection.cursor()
        q1 = "SELECT DISTINCT port FROM sw_data;"
        cursor.execute(q1)
        all_ports = cursor.fetchall()
        cursor.close()
        sqlite_connection.close()
        for a in all_ports:
            al.append(a[0].replace(f'{PORT_NAME}/', ''))

    except sqlite3.Error as error:
        al = [f'{error}']

    response = jsonify(al)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/speed/<port>')
def speed_port(port):
    try:
        sqlite_connection = sqlite3.connect('sw.db')
        cursor = sqlite_connection.cursor()
        port = f'{PORT_NAME}/0/{port}'

        v = (port, )
        q1 = "SELECT * FROM sw_data WHERE port = ? ORDER BY timestamp DESC LIMIT 1;"
        cursor.execute(q1, v)
        port_speed = cursor.fetchall()
        cursor.close()
        sqlite_connection.close()

    except sqlite3.Error as error:
        port_speed = [f'{error}']

    response = jsonify(port_speed)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/speed/<port>/last')
def speed_port_last(port):
    try:
        sqlite_connection = sqlite3.connect('sw.db')
        sqlite_connection.row_factory = dict_factory

        cursor = sqlite_connection.cursor()
        port = f'{PORT_NAME}/0/{port}'

        v = (port, )
        q1 = f"SELECT * FROM sw_data WHERE port = ? ORDER BY timestamp DESC LIMIT 100;"
        cursor.execute(q1, v)
        port_speed = cursor.fetchall()
        cursor.close()
        sqlite_connection.close()

    except sqlite3.Error as error:
        port_speed = [f'{error}']

    response = jsonify(port_speed)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/speed/<port>/<pid>')
def speed_port_id(port, pid):
    try:
        sqlite_connection = sqlite3.connect('sw.db')
        sqlite_connection.row_factory = dict_factory

        cursor = sqlite_connection.cursor()
        port = f'{PORT_NAME}/0/{port}'
        v = (port, pid)
        q1 = f"SELECT * FROM sw_data WHERE port = ? AND id > ? ORDER BY timestamp DESC;"
        cursor.execute(q1, v)
        port_speed = cursor.fetchall()
        cursor.close()
        sqlite_connection.close()

    except sqlite3.Error as error:
        port_speed = [f'{error}']

    response = jsonify(port_speed)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0")
