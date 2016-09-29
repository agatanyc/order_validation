from flask import Flask, request

from app import app
from model import Order, Error, init_db, db
import sqlite3

@app.route('/')
def index():
    return 'An awesome app to validate orders.'

@app.route('/orders/import', methods=['POST'])
def load_orders():
    data = request.data.strip().split('\n')
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
        o_state = mapped['state']
        o_zip_code = mapped['zipcode']
        # if order is valid populate valid column with `1` otherwise `0`.
        v = is_valid(line)
        if v:
            valid = 1
        else:
            valid = 0

        current_line = Order(order_id=order_id,
                                o_name=o_name,
                                o_email=o_email,
                                o_state=o_state,
                                o_zip_code=o_zip_code,
                                valid=valid,
                                errors=errors)
        db.session.add(current_line)
        db.session.commit()

    return 'Data loaded. To check for errors query orders.db errors table.' 
            #query ^^^^^^^ the db for errors and its user


def load_errors():
    pass

# Validation functions

def is_valid(line):
    # return 1 if order is valid, 0 otherwise
    rules = valid_state(line) and valid_zipcode(line), valid_age(line), valid_email(line), \
            valid_zip_sum(line), valid_domain(line), valid_automatically(line)
    return rules

def valid_state(line): # instatce of Order class
    print("made it in valid state!")
    """No wine can ship to New Jersey, Connecticut, Pennsylvania, Massachusetts,
    Illinois, Idaho or Oregon."""
    
    state = order.o_state 
    invalid_state = state in ('OR', 'NJ')
    if invalid_state:
        rule = 'Allowed states'
        new_row = Error(e_name=rule, order_key=order.primary_key)
        db.session.add(new_row)
        db.session.commit()
        return False
    return True   


def valid_zipcode(line):
    """Valid zip codes must be 5 or 9 digits."""
    return True

def valid_age(line):
    """Everyone ordering must be 21 or older."""
    return True

def valid_email(line):
    """ Email address must be valid."""
    return True

def valid_zip_sum(line):
    """The sum of digits in a zip code may not exceed 20
       ("90210": 9+0+2+1+0 = 12)."""
    return True

def valid_domain(line):
    """Customers from NY may not have .net email addresses."""
    return True

def valid_automatically(line):
    """If the state and zip code of the following record is 
    the same as the current record, it automatically passes."""
    return True



# mapped example:
# mapped = {'name': 'Stone Dominguez', 'zipcode': '05938',
#           'id': '4877', 'state': 'IA', 'birthday': 'Feb 27, 1963',
#          'email': 'ligula.Aliquam.erat@semperegestasurna.com'}


if __name__ == "__main__":
    app.debug = True

    init_db(app)
    app.run()

    
