from flask import Flask, render_template
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
app = Flask(__name__)

def proper_time(timestamp):
    # Parse the input timestamp and check if it has a timezone
    datetime_obj = datetime.fromisoformat(timestamp)
    if datetime_obj.tzinfo is not None and datetime_obj.tzinfo.utcoffset(datetime_obj) is not None:
        # If the timestamp has a timezone, convert it to UTC
        datetime_obj = datetime_obj.astimezone(pytz.UTC)
    
    # Convert the UTC datetime to Indian Standard Time (IST)
    ist_timezone = pytz.timezone("Asia/Kolkata")
    datetime_obj = datetime_obj.astimezone(ist_timezone)

    # Format the IST time as "HH:MM"
    formatted_time = datetime_obj.strftime("%H:%M")

    return formatted_time

def make_chart(timestamps,values,title):
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps,values, marker='o', linestyle='-', color='b')
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'static/{title}_chart.png')

def load_chart():
    channel_id = '2304996'
    api_key = 'H9R0CG8UOR23FG3B'
    results = '70'

    url = 'https://api.thingspeak.com/channels/{}/feeds.json'.format(channel_id)
    params = {'api_key': api_key, 'results': results}

    response = requests.get(url, params=params)

    # Check the response
    timestamps = []
    temperature_values = []
    humidity_values = []
    rainfall_values =[]
    smoke_values = []
    if response.status_code == 200:
        data = response.json()
        print(data)
        for entry in data['feeds']:
            timeval = proper_time(entry['created_at'])
            tempval = entry['field1'] if entry['field1'] != None else "37.5"
            humval = entry['field2'] if entry['field2'] != None else "0"
            rainval = entry['field3'] if entry['field3'] != None else "0"
            smokeval = entry['field4'] if entry['field4'] != None else "0"
            print(timeval,tempval,humval,rainval,smokeval)
            timestamps.append(timeval)
            temperature_values.append(float(tempval))
            humidity_values.append(float(humval))
            rainfall_values.append(float(rainval))
            smoke_values.append(float(smokeval))
    make_chart(timestamps,temperature_values,'Temperature')
    make_chart(timestamps,humidity_values,'Humidity')
    make_chart(timestamps,rainfall_values,'Rainfall')
    make_chart(timestamps,rainfall_values,'Smoke')



@app.route('/')
def index():
    load_chart()
    return render_template('basic.html')

if __name__ == '__main__':
    app.run(debug=True)

