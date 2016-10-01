from flask import Flask, request

from app import app
from model import Order, Error, init_db, db
import sqlite3
from datetime import datetime
from validate_email import validate_email

@app.route('/')
def index():
    return 'An awesome app to validate orders.'

@app.route('/orders/import', methods=['POST'])
def load_orders():
    data = request.data.strip().split('\n')
    if len(data) > 1:
        columns = data[0].strip().split('|')
        current_line = None
        for line in data[1:]:
            split_line = line.strip().split('|')
            # mapped example:
            # mapped = {'name': 'Stone Dominguez', 'zipcode': '05938',
            #           'id': '4877', 'state': 'IA', 'birthday': 'Feb 27, 1963',
            #          'email': 'ligula.Aliquam.erat@semperegestasurna.com'}
            mapped = {}
            for i in range(len(columns)):
                mapped[columns[i]] = split_line[i]
            # populate `Order` table
            order_id = mapped['id']
            o_name = mapped['name']
            o_email = mapped['email']
            o_state = mapped['state']
            o_zip_code = mapped['zipcode']
            o_DOB = mapped['birthday']
            next_line = Order(order_id=order_id,
                                    o_name=o_name,
                                    o_email=o_email,
                                    o_state=o_state,
                                    o_zip_code=o_zip_code,
                                    o_DOB = o_DOB,
                                    valid=0,
                                    errors=[])
            # if order is valid populate valid column with `1` otherwise `0`.
            # set_valid(current_line, next_line)
            if current_line:
                set_valid(current_line, next_line)
                db.session.add(current_line)
                db.session.commit()
            current_line = next_line
        set_valid(current_line, None)
        db.session.add(current_line)
        db.session.commit()
# TODO return JSON
    return 'Data loaded. To check for errors query orders.db errors table.' 


# Validation functions

def set_valid(line, next_line):
    """Return False if any of the validation functions return False,
        otherwise True.
        If the state and zip code of the following record is 
        the same as the current record, it automatically passes."""
    if next_line and line.o_zip_code == next_line.o_zip_code and \
         line.o_state == next_line.o_state:
         line.valid = 1
    else:
        state_valid = valid_state(line)
        zipcode_valid = valid_zipcode(line)
        age_valid = valid_age(line)
        email_valid = valid_email(line)
        zip_sum_valid = valid_zip_sum(line)
        domain_valid = valid_domain(line)
        if state_valid and zipcode_valid and age_valid and email_valid and \
           zip_sum_valid and domain_valid:
            line.valid = 1
        else:
            line.valid = 0
    return line.valid

def valid_state(line): # instatce of Order class
    """No wine can ship to New Jersey, Connecticut, Pennsylvania, Massachusetts,
    Illinois, Idaho or Oregon."""
    state = line.o_state 
    invalid_state = state in ('NJ', 'PA', 'MA', 'IL', 'CT', 'ID', 'OR',)
    if invalid_state:
        rule = 'Allowed states'
        new_row = Error(e_name=rule, order_key=line.primary_key)
        line.errors.append(new_row)
        return False
    return True   


def valid_zipcode(line):
    """Valid zip codes must be 5 or 9 digits."""
    zipcode = line.o_zip_code
    invalid_zip = len(zipcode) not in [5, 9] and zipcode.isdigit()
    if invalid_zip:
        rule = 'Zipcode length'
        new_row = Error(e_name=rule, order_key=line.primary_key)
        line.errors.append(new_row)
        return False
    return True

def _is_21(dob):
    # date of birth format example: "Sep 30, 1995"
    today = datetime.today()
    threshold = datetime(today.year - 21, today.month, today.day)
    test = datetime.strptime(dob, "%b %d, %Y")
    if test <= threshold:
        return True
    else:
        return False
       
def valid_age(line):
    """Everyone ordering must be 21 or older."""
    dob = line.o_DOB
    if not _is_21(dob):
        rule = 'Allowed age'
        new_row = Error(e_name=rule, order_key=line.primary_key)
        line.errors.append(new_row)
        return False
    return True

def valid_email(line):
    """ Email address must be valid."""
    email = line.o_email
    is_valid = validate_email(email)
    if not is_valid:
        rule = 'Email validation'
        new_row = Error(e_name=rule, order_key=line.primary_key)
        line.errors.append(new_row)
        return False
    return True

def valid_zip_sum(line):
    """The sum of digits in a zip code may not exceed 20
       ("90210": 9+0+2+1+0 = 12)."""
    zipcode = line.o_zip_code
    if not sum(int(x) for x in zipcode) <= 20:
        rule = 'Zipcode sum'
        new_row = Error(e_name=rule, order_key=line.primary_key)
        line.errors.append(new_row)
        return False
    return True

def valid_domain(line):
    """Customers from NY may not have .net email addresses."""
    email = line.o_email
    ln = len(email)
    invalid_domain = (email[ln - 4:] == '.net')
    invalid_state = (line.o_state == 'NY')
    if invalid_domain and invalid_state:
        rule = '.net domain'
        new_row = Error(e_name=rule, order_key=line.primary_key)
        line.errors.append(new_row)
        return False
    return True

if __name__ == "__main__":
    app.debug = True

    init_db(app)
    app.run()

    
