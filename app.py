# import the Flask Framework
from flask import Flask, jsonify, make_response, request
import requests
import secrets
import eventlet.wsgi
import logging

logging.basicConfig(filename="mpesa.log",filemode="a",format='%(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

ip = "68.183.89.127"
# You may create a separate URL for every endpoint you need

@app.route('/mpesa/b2c/v1', methods=["POST"])
def listenb2c():
    # save the data
    request_data = request.data
    logging.info("Callback url called with the data ", request_data)
    decoded = request_data.decode()
    # Perform your processing here e.g. print it out...
    requests.post(f"http://{ip}:9000/payment/status", json=decoded)

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

