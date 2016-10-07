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
        #print 'IIIIIIII INDEX', response.data
        self.assertEqual(response.status_code, 200)

    def test_load_orders(self):
        # mock fucionality of the app
        tester = app.test_client(self)
        response = tester.post('/orders/import')
        #print 'XxxxxxxxxxxxXXXXXXXXX LOAD ORDERS ALL', response.data
        self.assertEqual(response.status_code, 200)

    def test_orders(self):
        tester = app.test_client(self)
        response = tester.get('/orders/')
        # expecct data to be a list of one dictionary
        data = json.loads(response.data)
        order_data = data[0]
        self.assertEqual(order_data['order_id'], 4877)
        #print  'RRRRRRRRRRRRR ORDRS 3', dict(data)
        """
        new_line = Order(order_id=1,
                                    o_name='agata',
                                    o_email='agata@gmail.com',
                                    o_state='NY',
                                    o_zip_code='11217',
                                    o_DOB = 11.09.84,
                                    valid=0,
                                    errors=[])
        

        db.session.add(new_line)
        db.session.commit()
        """
    def tearDown(self):
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()
