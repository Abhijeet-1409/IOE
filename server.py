from flask import Flask, render_template, jsonify
import json
from flask_cors import CORS, cross_origin
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import threading
import time

app = Flask(__name__)  # Fix the app creation
CORS(app, resources={r"/": {"origins": "*"}})
app.config["CORS_HEADERS"] = "Content-Type"


def customCallback(client, userdata, message):
    print("Callback came...")
    print("Topic: " + message.topic)
    payload = message.payload.decode()
    print("Message: " + payload)

    # Save the received data to a JSON file
    # save_to_json(payload)
    # Use a timer to introduce a delay before processing the data
    delay_timer = threading.Timer(30, save_to_json, args=(payload,))
    delay_timer.start()


def save_to_json(data):
    try:
        with open("received_data.json", "a") as json_file:
            json.dump(data, json_file)
            json_file.write("\n")
        print("Data saved to received_data.json")
    except Exception as e:
        print("Error saving data to JSON file:", str(e))


def periodic_callback():
    myMQTTClient = AWSIoTMQTTClient("device")
    myMQTTClient.configureEndpoint(
        "asilr3wvsr3fd-ats.iot.us-east-1.amazonaws.com", 8883
    )
    myMQTTClient.configureCredentials(
        "AmazonRootCA1.pem", "Private_key.key", "certificate.crt"
    )

    myMQTTClient.connect()
    print("Client Connected")

    while True:
        # Subscribe to the analytics_topic with QoS 1
        myMQTTClient.subscribe("esp32/pub", 1, customCallback)

        time.sleep(5)  # Sleep for 5 seconds


@app.route("/")
def index():
    myMQTTClient = AWSIoTMQTTClient("device")
    myMQTTClient.configureEndpoint(
        "asilr3wvsr3fd-ats.iot.us-east-1.amazonaws.com", 8883
    )

    myMQTTClient.configureCredentials(
        "AmazonRootCA1.pem", "Private_key.key", "certificate.crt"
    )

    myMQTTClient.connect()
    print("Client Connected")

    # Subscribe to the analytics_topic with QoS 1
    myMQTTClient.subscribe("esp32/pub", 1, customCallback)
    print("Waiting for the callback. Press Enter to continue...")

    return render_template("index.html")


@app.route("/get_data")
def get_data():
    # Read data from the JSON file
    data_list = []
    with open("received_data.json", "r") as json_file:
        for line in json_file:
            data_list.append(json.loads(line))
    send_list = []
    for data in data_list:
        send_list.append(json.loads(data))

    return send_list


@app.route("/get_json")
@cross_origin()
def get_json():
    # Read data from the JSON file
    data_list = []
    with open("received_data.json", "r") as json_file:
        for line in json_file:
            data_list.append(json.loads(line))

    # Parse the JSON strings and create a list of dictionaries
    parsed_data = [json.loads(item) for item in data_list]

    # Convert the list of dictionaries to a properly formatted JSON array
    formatted_json = json.dumps(parsed_data, indent=4)

    return formatted_json  # Read data from the JSON file


if __name__ == "_main_":
    background_thread = threading.Thread(target=periodic_callback)
    background_thread.daemon = True
    background_thread.start()
    app.run(debug=True)
