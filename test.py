from app import app
from model import db
import server
from server import *
from model import Order

import unittest
import json

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.create_all()
        tester = app.test_client(self)
        response = tester.post('/orders/import', content_type='application/json',
        data = 'id|name|email|state|zipcode|birthday\n' +  \
                   '4877|Stone Dominguez|ligula.Aliquam.erat@semperegestasurna.com|OR|05938|Feb 27, 1963')
         

    # Ensure that flask was set up correctly
    def test_index(self):
        # mock fucionality of the app
        tester = app.test_client(self)
        # check response from the app
        response = tester.get('/', content_type='text/plain')
        self.assertEqual(response.status_code, 200)

    def test_load_orders(self):
        # mock fucionality of the app
        tester = app.test_client(self)
        response = tester.post('/orders/import')
        self.assertEqual(response.status_code, 200)

    def test_orders(self):
        tester = app.test_client(self)
        response = tester.get('/orders/')
        # expecct data to be a list of one dictionary
        data = json.loads(response.data)
        order_data = data[0]
        self.assertEqual(order_data['order_id'], 4877)

    def test_allowed_states_error(self):
        tester = app.test_client(self)
        response = tester.get('/orders/4877')
        data = json.loads(response.data)
        order_data = data[0]
        error_data = order_data['errors']
        error_name = error_data[0]['e_name']
        self.assertEqual(error_name, 'Allowed states')
        print error_data


    def tearDown(self):
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()
