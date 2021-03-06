from flask import Flask, request, jsonify, json

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
    orders = db.session.query(Order).all()

    result = []
    for order in orders:
        errors = []
        for error in order.errors:
            errors.append({'primary_key':error.primary_key,
                            'e_name':error.e_name,
                            'order_key':error.order_key})

        result.append({'primary_key':order.primary_key,
                    'order_id':order.order_id,
                    'o_name':order.o_name,
                    'o_email':order.o_email,
                    'o_state':order.o_state,
                    'o_zip_code':order.o_zip_code,
                    'o_DOB':order.o_DOB,
                    'valid':order.valid,
                    'errors':errors})

    return jsonify(result)

    #return 'Data loaded. To check for errors query orders.db errors table.' 

@app.route('/orders/', methods=['GET'])
@app.route('/orders/<order_id>', methods=['GET'])
def orders(order_id=None):
    """Return imported orders info depending on the request."""

    # give detailed information about a given order
    flag = request.args.get('valid')
    if order_id:
        detailed_orders = db.session.query(Order).filter(
                                              Order.order_id == order_id)
        result = []
        for order in detailed_orders:
            errors = []
            for error in order.errors:
                if error.e_name == 'Allowed states':
                    message = 'We dont ship to ' + order.o_state
                elif error.e_name == 'Zipcode sum':
                    message = 'The sum of digits in a zip code may not exceed 20'
                elif error.e_name == 'Zipcode length':
                    message = 'Valid zip codes must be 5 or 9 digits'
                elif error.e_name == 'Allowed age':
                    message = 'Everyone ordering must be 21 or older'
                elif error.e_name == 'Email validation':
                    message =  'Email address must be valid'
                elif error.e_name == '.net domain':
                    message = 'Customers from NY may not have .net email addresses.'
                else:
                    message = 'Unknown error'

                errors.append({
                            'e_name':error.e_name,
                            'message': message
                            })

            result.append({'primary_key':order.primary_key,
                        'order_id':order.order_id,
                        'o_name':order.o_name,
                        'o_email':order.o_email,
                        'o_state':order.o_state,
                        'o_zip_code':order.o_zip_code,
                        'o_DOB':order.o_DOB,
                        'valid':order.valid,
                        'errors':errors})
        return jsonify(result)
    # filter order by validity (e.g. /orders?valid=1)
    elif flag == '1':
        orders = db.session.query(Order).filter(Order.valid == 1).all()
    elif flag == '0':
        orders = db.session.query(Order).filter(Order.valid == 0).all()
    # provide selected info about order
    else:
        orders = db.session.query(Order).all()
    result = []
    for order in orders:
        result.append({'order_id': order.order_id,
                  'name':order.o_name,
                  'valid':order.valid})
    return jsonify(result)

    
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
        if app.config.get('ALLOWED_STATES'):
            state_valid = valid_state(line)
        else:
            state_valid = True
        if app.config.get('ZIPCODE_LENGTH'):
            zipcode_valid = valid_zipcode(line)
        else:
            zipcode_valid = True
        if app.config.get('ALOWED_AGE'):
            age_valid = valid_age(line)
        else:
            age_valid = True
        if app.config.get('EMAIL_VALIDATION'):
            email_valid = valid_email(line)
        else:
            email_valid = True
        if app.config.get('ZIPCODE_SUM'):
            zip_sum_valid = valid_zip_sum(line)
        else:
            zip_sum_valid = True
        if app.config.get('ZIPCODE_SUM'):
            domain_valid = valid_domain(line)
        else:
            domain_valid = True
        if state_valid and zipcode_valid and age_valid and email_valid and \
           zip_sum_valid and domain_valid:
            line.valid = 1
        else:
            line.valid = 0
    return line.valid

def valid_state(line): # line is an instance of Order class
    """No wine can ship to New Jersey, Connecticut, Pennsylvania, Massachusetts,
    Illinois, Idaho or Oregon."""
    state = line.o_state 
    invalid_state = state in app.config.get('ALLOWED_STATES')
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

    
