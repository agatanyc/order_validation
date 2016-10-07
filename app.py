from flask import Flask

# create the aplication
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config.update(
    DEBUG=True,
    ALLOWED_STATES=['NJ', 'PA', 'MA', 'IL', 'CT', 'ID', 'OR'],
    ZIPCODE_SUM=True,
    ZIPCODE_LENGTH= True,
    ALLOWED_AGE=True,
    EMAIL_VALIDATION=True,
    NET_DOMAIN=True
)

