:# order_validation
Order validation and management service  that is used to determine if a data 
set of orders are considered valid.

## dependencies
python2

flask

sqlite3

validate email

## to run the code (on local host):

`python model.py` (to initialize db and create tables)

`python server.py`  ( to start the server)


### you can use Advanced REST client (chrome extension) to send requests.

## example of the order data can be found in `data.txt`

## to query the db from command line run:

`python model.py`

sqlite3 orders.db

## Deployment

TBD


## Tests - WORK IN PROGRESS
