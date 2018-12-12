# Import SDK packages

# Microsoft packages
# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

# Python packages
from uuid import getnode as get_mac
import json
import random
import ssl
import time
import configparser
from decimal import Decimal
import argparse
# DHT22 packages
import Adafruit_DHT

# Using the MQTT protocol.
PROTOCOL = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT = 10000

def get_configurations():
    '''Read configurations from the ini file'''
    # Read parameters from config file
    # Config file needs to be in same folder as this
    config = configparser.ConfigParser()
    config.read('config.ini')
    connection = config['default']['connection']
    return connection


def set_up_azure_connection(connection):
    # Create an IoT Hub client
    client = IoTHubClient(connection, PROTOCOL)
    return client


def get_payload(sensor, pin, iccid):
    '''User adafruit library to read data from DHT 22 sensor'''
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    # round to one decimal
    humidity = round(Decimal(humidity),1)
    temperature = round(Decimal(temperature),1)
    # create payload
    payload = {
        'device_id': hex(get_mac()),
        'temp': temperature,
        'hum': humidity,
        'time': int(round(time.time()*1000)),
        'iccid': iccid
        }
    print(payload)
    return payload


def get_payload_random(iccid):
    '''If no sensor is connected, generate the data'''
    payload = {
        'device_id': hex(get_mac()),
        'temp': round(random.uniform(18,25), 1),
        'hum': round(random.uniform(20,80), 1),
        'time': int(round(time.time()*1000)),
        'iccid': iccid
        }
    print(payload)
    return payload


def send_confirmation_callback(message, result, user_context):
    print ( "IoT Hub responded to message with status: %s" % (result) )


def read_sensor_data(mqttClient, sensor, pin, iccid, random):
    '''Loop that send the data to AWS'''
    while True:
        # Send payload
        if random == 't':
            message = IoTHubMessage(json.dumps(get_payload_random(iccid)))
        else:
            message = IoTHubMessage(json.dumps(get_payload(sensor, pin, iccid)))
        mqttClient.send_event_async(message, send_confirmation_callback, None)
        # delay 30 seconds before running next
        time.sleep(30)


if __name__=="__main__":
    '''Main function'''
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pin", 
        help="Which Raspberry Pi bin the dht22 is connected to", 
        default=2)
    parser.add_argument("-r", "--random", 
        help="Generates random values if no sensor is available", 
        default='f', 
        choices=['f','t'])
    parser.add_argument("-i", "--iccid", 
        help="ICCID of the SIM that is used for connectivity", 
        default='123456789')
    args = parser.parse_args()
    sensor = Adafruit_DHT.DHT22
    pin = args.pin
    iccid = args.iccid
    # Encode the connection string with utf-8
    connection = get_configurations()
    connection_str = connection.encode('utf8','ignore')
    # Set up azure connection
    mqttClient = set_up_azure_connection(connection_str)
    # Read sensor data and send it to azure
    read_sensor_data(mqttClient, sensor, pin, iccid, args.random)
