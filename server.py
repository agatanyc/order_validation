from flask import Flask, request

from app import app
from model import Order, Error, init_db, db
import sqlite3

@app.route('/')
def index():
    return 'An awesome app to validate orders.'

@app.route('/orders/import', methods=['POST'])
def load_orders():
    data = request.data.split('\n')
    print 'DATA: ', data
    columns = data[0].split('|')
    print 'COLUMNS', columns
    for line in data[1:]:
        split_line = line.split('|')
        mapped = {}
        for i in range(len(columns)):
            mapped[columns[i]] = split_line[i]
        # populate `Order` table
        order_id = mapped['id']
        o_name = mapped['name']
        o_email = mapped['email']
        o_zip_code = mapped['zipcode']
        valid = is_valid(line)
        errors=[]

        current_entry = Order(order_id=order_id,
                                o_name=o_name,
                                o_email=o_email,
                                o_zip_code=o_zip_code,
                                valid=valid,
                                errors=errors)
        db.session.add(current_entry)
        db.session.commit()
    return 'Data loaded. To check for potential errors go to: ' #TODO
            #query ^^^^^^^ the db for errors and its user


def load_errors():
    if errors: #TODO is_valid will return collection of errors if any
        for error in errors:
            e_name = error

# Validation functions

def is_valid(line):
    # return 1 if order is valid, 0 otherwise
    return True

def valid_state():
    return True

def valid_zipcode():
    return True



# mapped example:
# mapped = {'name': 'Stone Dominguez', 'zipcode': '05938',
#           'id': '4877', 'state': 'IA', 'birthday': 'Feb 27, 1963',
#          'email': 'ligula.Aliquam.erat@semperegestasurna.com'}


if __name__ == "__main__":
    app.debug = True

    init_db(app)
    app.run()
