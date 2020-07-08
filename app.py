# import the Flask Framework
from flask import Flask, jsonify, make_response, request
import requests
import secrets
import eventlet.wsgi
import logging

from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

logging.basicConfig(filename="mpesa.log", filemode="a", format='%(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# basedir  = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:japanitoes@localhost:3306/fuprox"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

ip = "68.183.89.127"


# paymnets schema

class Payments(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    body = db.Column(db.Text, nullable=False)

    def __init__(self, body):
        self.body = body


class PaymentSchema(ma.Schema):
    class Meta:
        fields = ("id", "message")


class Mpesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=True)
    receipt_number = db.Column(db.String(255), nullable=True)
    transaction_date = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.Integer, nullable=True)
    checkout_request_id = db.Column(db.String(255), nullable=True)
    merchant_request_id = db.Column(db.String(255), nullable=True)
    result_code = db.Column(db.Integer, nullable=False)
    result_desc = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime(), default=datetime.now)
    local_transactional_key = db.Column(db.String(255), nullable=False)

    def __init__(self, MerchantRequestID, CheckoutRequestID, ResultCode, ResultDesc):
        self.merchant_request_id = MerchantRequestID
        self.checkout_request_id = CheckoutRequestID
        self.result_code = ResultCode
        self.result_desc = ResultDesc


class MpesaSchema(ma.Schema):
    class Meta:
        fields = ("id", "amount", "receipt_number", "transaction_date", "phone_number", "checkout_request_id",
                  "merchant_request_id", "result_code", "result_desc", "date_added", "local_transactional_key")


# You may create a separate URL for every endpoint you need

@app.route('/mpesa/b2c/v1', methods=["POST"])
def listenb2c():
    # save the data
    request_data = request.data
    print(request_data)
    lookup = Payments(request_data)
    db.session.add(lookup)
    db.session.commit()

    logging.info("Callback url called with the data ", request_data)
    decoded = request_data.decode()

    # Perform your processing here e.g. print it out...
    requests.post(f"http://{ip}:4000/payment/status", json=decoded)

    # here we are going to emit and event for the key
    # Prepare the response, assuming no errors have occurred. Any response
    # other than a 0 (zero) for the 'ResultCode' during Validation only means
    # an error occurred and the transaction is cancelled

    message = {
        "ResultCode": 0,
        "ResultDesc": "The service was accepted successfully",
        "ThirdPartyTransID": secrets.token_hex()
    }
    # Send the response back to the server
    return jsonify({'message': message}), 200


print("?????running")

@app.route("/mpesa/reversals", methods=["POST"])
def reversals():
    print("we hae been hit")
    # save the data
    request_data = request.data
    logging.info("Callback url called with the data ", request_data)
    decoded = request_data.decode()
    # Perform your processing here e.g. print it out...
    requests.post(f"http://{ip}:4000/payment/status/reversal", json=decoded)

    # here we are going to emit and event for the key
    # Prepare the response, assuming no errors have occurred. Any response
    # other than a 0 (zero) for the 'ResultCode' during Validation only means
    # an error occurred and the transaction is cancelled
    message = {
        "ResultCode": 0,
        "ResultDesc": "The service was accepted successfully",
        "ThirdPartyTransID": secrets.token_hex()
    }
    # Send the response back to the server
    return jsonify({'message': message}), 200


# Change this part to reflect the API you are testing
@app.route('/mpesa/b2b/v1')
def listenb2b():
    request_data = request.data
    print(request_data)
    message = {
        "ResultCode": 0,
        "ResultDesc": "The service was accepted successfully",
        "ThirdPartyTransID": "1234567890"
    }
    return message


if __name__ == '__main__':
    # app.run(debug=True,port="8080")
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
