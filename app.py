# Zoe Strachan, Group 2

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
import sqlite3
import hmac


class Admin(object):
    def __init__(self, full_name, username, password):
        self.name = full_name
        self.user = username
        self.password = password


class Patron(object):
    def __init__(self, patron_id, full_name, email_address, contact_details, address, banking_details, username, password):
        self.id = patron_id
        self.name = full_name
        self.email = email_address
        self.contact = contact_details
        self.address = address
        self.banking = banking_details
        self.user = username
        self.password = password


class Reservation(object):
    def __init__(self, reservation_id, full_name, email_address, price, reservation_time, reservation_date, seats):
        self.id = reservation_id
        self.name = full_name
        self.email = email_address
        self.price = price
        self.time = reservation_time
        self.date = reservation_date
        self.seat = seats


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("reservations.db")
        self.cursor = self.conn.cursor()


def init_admin_table():
    conn = sqlite3.connect('reservations.db')
    print("Opened database")

    conn.execute("CREATE TABLE IF NOT EXISTS admin (admin_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "full_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("Admin table created")
    conn.close()
    return init_admin_table


def init_patron_table():
    with sqlite3.connect("reservations.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS patron(patron_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "full_name TEXT NOT NULL,"
                     "email_address TEXT NOT NULL,"
                     "contact_number INTEGER NOT NULL,"
                     "address TEXT NOT NULL,"
                     "banking_details INTEGER NOT NULL,"
                     "username TEXT NOT NULL,"
                     "password TEXT NOT NULL)")
        print("Patron table created")
    conn.close()
    return init_patron_table


def init_reservation_table():
    with sqlite3.connect("reservations.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS reservation (res_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "full_name TEXT NOT NULL,"
                     "email_address TEXT NOT NULL,"
                     "price INTEGER NOT NULL,"
                     "reservation_date DATE,"
                     "reservation_time TIME,"
                     "seats INTEGER NOT NULL)")
        print("Reservation table created")
    conn.close()
    return init_reservation_table


def fetch_patron():
    with sqlite3.connect('reservations.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM patron")
        patron = cursor.fetchall()

        new_patron = []
        for data in patron:
            new_patron.append(Admin(data[0], data[6], data[4]))
        return new_patron


def fetch_admin():
    with sqlite3.connect('reservations.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM admin")
        admin = cursor.fetchall()

        new_admin = []
        for data in admin:
            new_admin.append(Admin(data[0], data[1], data[2]))
        return new_admin


init_admin_table()
init_patron_table()
init_reservation_table()
admin = fetch_admin()
patron = fetch_patron()

admin_table = {p.user: p for p in admin}
patron_id_table = {p.name: p for p in admin}


def authenticate(username, password):
    patron = patron_id_table.get(username, None)
    if patron and hmac.compare_digest(patron.password.encode('utf-8'), password.encode('utf-8')):
        return patron


def identity():
    patron_id = ['identity']
    return patron_id_table.get(patron_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/admin_registration/', methods=["POST"])
def admin_registration():
    response = {}
    if request.method == "POST":
        full_name = request.json["full_name"]
        username = request.json["username"]
        password = request.json["password"]
        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO admin("
                           "full_name,"
                           "username,"
                           "password) VALUES(?, ?, ?)",
                           (full_name, username, password))
            conn.commit()
            response['message'] = "Admin Registered"
            response['status_code'] = 201
            response['data'] = {
                "full_name": full_name,
                "username": username,
                "password": password
            }
            return response


@app.route('/admin_login', methods=["PATCH"])
def admin_login():
    response = {}
    if request.method == "PATCH":
        username = request.json["username"]
        password = request.json["password"]

        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
            admin = cursor.fetchone()
        response['status_code'] = 200
        response['data'] = admin
        return response
    else:
        if request.method != "POST":
            response['message'] = "Incorrect Method"
            response['status_code'] = 400
            return response


@app.route('/patron_registration/', methods=["POST"])
def patron_registration():
    response = {}

    if request.method == "POST":
        full_name = request.json['full_name']
        email_address = request.json['email_address']
        contact_number = request.json['contact_number']
        address = request.json['address']
        banking_details = request.json['banking_details']
        username = request.json['username']
        password = request.json['password']

        with sqlite3.connect('reservations.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO patron("
                           "full_name,"
                           "email_address,"
                           "contact_number,"
                           "address,"
                           "banking_details,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (full_name, email_address, contact_number, address, banking_details, username, password))
            conn.commit()
            response["message"] = "Registration Complete"
            response["status_code"] = 201
        return response


@app.route('/patron_login', methods=["PATCH"])
def patron_login():
    response = {}
    if request.method == "PATCH":
        username = request.json["username"]
        password = request.json["password"]

        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patron WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
        response['status_code'] = 200
        response['data'] = user
        return response
    else:
        if request.method != "POST":
            response['message'] = "Incorrect Method"
            response['status_code'] = 400
            return response


@app.route('/view-patron/<int:patron_id>', methods=['GET'])
def view_patron(patron_id):
    response = {}

    with sqlite3.connect("reservations.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patron WHERE patron_id=" + str(patron_id))
        response["status_code"] = 200
        response["description"] = "Patron retrieved"
        response["data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/edit-patron/<int:patron_id>', methods=["PUT"])
def edit_patron(patron_id):
    response = {}
    if request.method == "PUT":
        with sqlite3.connect("reservations.db") as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("full_name") is not None:
                put_data["full_name"] = incoming_data.get("full_name")
                with sqlite3.connect("reservations.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE patron SET full_name=? WHERE patron_id=?', (put_data["full_name"], patron_id))
                    conn.commit()
                    response['message'] = "Edit complete"
                    response['status_code'] = 200
                return response

            if incoming_data.get('email_address') is not None:
                put_data['email_address'] = incoming_data.get('email_address')
                with sqlite3.connect('reservations.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE patron email=? WHERE patron_id=?', (put_data['email_address'], patron_id))
                    conn.commit()
                    response['message'] = "Edit complete"
                    return response

            if incoming_data.get("contact_number") is not None:
                put_data["contact_number"] = incoming_data.get("contact_number")
                with sqlite3.connect("reservations.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE patron SET contact_number=? WHERE patron_id=?',
                                   (put_data["contact-number"], patron_id))
                    conn.commit()
                    response['message'] = "Edit complete"
                    response['status_code'] = 200

            if incoming_data.get('address') is not None:
                put_data['address'] = incoming_data.get('address')
                with sqlite3.connect('reservations.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE patron address=? WHERE patron_id=?', (put_data['address'], patron_id))
                    conn.commit()
                    response['message'] = "Edit complete"
                    return response

            if incoming_data.get('banking_details') is not None:
                put_data['banking_details'] = incoming_data.get('banking_details')
                with sqlite3.connect('reservations.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE patron banking_details=? WHERE patron_id=?',
                                   (put_data['banking_details'], patron_id))
                    conn.commit()
                    response['message'] = "Edit complete"
                    return response

            if incoming_data.get('username') is not None:
                put_data['username'] = incoming_data.get('username')
                with sqlite3.connect('reservations.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE patron username=? WHERE patron_id=?', (put_data['username'], patron_id))
                    conn.commit()
                    response['message'] = "Edit complete"
                    return response

            if incoming_data.get('password') is not None:
                put_data['password'] = incoming_data.get('password')
                with sqlite3.connect('reservations.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE patron password=? WHERE patron_id=?', (put_data['password'], patron_id))
                    conn.commit()
                    response['message'] = "Edit complete"
                    return response


@app.route('/delete-patron/<int:patron_id>', methods=["DELETE"])
def delete_patron(patron_id):
    response = {}
    if request.method == "DELETE":
        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patron WHERE patron_id=" + str(patron_id))
            conn.commit()

            response['status_code'] = 200
            response['message'] = "Patron removed."
        return response


@app.route('/create-reservation', methods=['POST'])
def create_reservation():
    response = {}

    if request.method == "POST":
        full_name = request.json['name']
        email_address = request.json['email_address']
        price = request.json['price']
        reservation_time = request.json['reservation_time']
        reservation_date = request.json['reservation_date']
        seats = request.json['seats']

        with sqlite3.connect('reservations.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO reservation("
                           "full_name,"
                           "email_address,"
                           "price,"
                           "reservation_time,"
                           "reservation_date,"
                           "seats) VALUES(?, ?, ?, ?, ?, ?)",
                           (full_name, email_address, price, reservation_time, reservation_date, seats))
            conn.commit()
            response["message"] = "Reservation booked."
            response["status_code"] = 200
        return response


@app.route('/view-reservation/<int:reservation_id>', methods=['GET'])
def view_reservation(reservation_id):
    response = {}
    with sqlite3.connect("reservations.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservation WHERE res_id=" + str(reservation_id))
        res = cursor.fetchone()
        response['data'] = res
        response['status_code'] = 200
        response['message'] = "Reservation retrieved"
    return response


@app.route('/edit-reservation/<int:reservation_id>', methods=["PUT"])
def edit_reservation(reservation_id):
    response = {}
    if request.method == "PUT":
        with sqlite3.connect("reservations.db") as conn:
            incoming_data = dict(request.json)
            put_data = {}

    if incoming_data.get("full_name") is not None:
        put_data["full_name"] = incoming_data.get("full_name")
        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reservation SET full_name=? WHERE res_id=?",
                           (put_data["full_name"], reservation_id))
            conn.commit()
            response['message'] = "Edit Complete"
            response['status_code'] = 200
            return response

    if incoming_data.get("email_address") is not None:
        put_data["email_address"] = incoming_data.get("email_address")
        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reservation SET email_address=? WHERE res_id=?",
                           (put_data["email_address"], reservation_id))
            conn.commit()
            response['message'] = "Edit Complete"
            response['status_code'] = 200
            return response

    if incoming_data.get("reservation_time") is not None:
        put_data["reservation_time"] = incoming_data.get("reservation_time")
        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reservation SET reservation_time=? WHERE res_id=?",
                           (put_data["reservation_time"], reservation_id))
            conn.commit()
            response['message'] = "Edit Complete"
            response['status_code'] = 200

    if incoming_data.get("reservation_date") is not None:
        put_data["reservation_date"] = incoming_data.get("reservation_date")
        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reservation SET reservation_date=? WHERE res_id=?",
                           (put_data["reservation_date"], reservation_id))
            conn.commit()
            response['message'] = "Edit Complete"
            response['status_code'] = 200

    if incoming_data.get('seats') is not None:
        put_data['seats'] = incoming_data.get('seats')
        with sqlite3.connect('reservation.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE reservation SET seats=? WHERE res_id=?', (put_data['seats'], reservation_id))
            conn.commit()
            response['message'] = "Edit Complete"
            return response


@app.route('/delete-reservation/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    response = {}
    with sqlite3.connect("reservations.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservation WHERE res_id=" + str(reservation_id))
        conn.commit()

        response['status_code'] = 200
        response['message'] = "Reservation removed."
    return response


if __name__ == '__main__':
    app.run()
