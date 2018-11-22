# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import DROP_OLDEST
from uuid import getnode as get_mac
import json
import random
import ssl
import time
import configparser
from decimal import Decimal
import argparse
# This is for reading the DHT22
import Adafruit_DHT

def get_configurations():
    '''Read configurations from the ini file'''
    # Read parameters from config file
    # Config file needs to be in same folder as this
    config = configparser.ConfigParser()
    config.read('config.ini')
    clientId = config['default']['clientId']
    endpoint = config['default']['endpoint']
    aws_root_cert = config['default']['aws_root_cert']
    private_key = config['default']['private_key']
    cert = config['default']['cert']
    data_topic = config['default']['data_topic']
    return clientId, endpoint, aws_root_cert, private_key, cert, data_topic

def set_up_aws_connection(clientId, endpoint, aws_root_cert, private_key, cert):
    '''Set up the connection parameters to AWS'''
    # Disable the metrics collection
    # AWSIoTMQTTClient.disableMetricsCollection()
    # For certificate based connection
    MQTTClient = AWSIoTMQTTClient(clientId)
    # Configurations
    # For TLS mutual authentication
    MQTTClient.configureEndpoint(endpoint, 8883)
    # For TLS mutual authentication with TLS ALPN extension
    MQTTClient.configureCredentials(aws_root_cert, private_key, cert)
    # Parameters
    # Offline queing, queue save 10 messages and drop oldest ones
    MQTTClient.configureOfflinePublishQueueing(10, DROP_OLDEST)
    # Draining: 2 Hz, this needs to be shorter than the data collection period! 
    # 10 messages at 2 Hz is 20 seconds
    MQTTClient.configureDrainingFrequency(2)  
    # 2 min
    MQTTClient.configureConnectDisconnectTimeout(120)  
    # 5 sec
    MQTTClient.configureMQTTOperationTimeout(5)  
    # AWS IoT MQTT Client auto reconnect backofftime
    #AWSIoTPythonSDK.MQTTLib.AWSIoTMQTTClient.configureAutoReconnectBackoffTime(baseReconnectQuietTimeSecond, maxReconnectQuietTimeSecond, stableConnectionTimeSecond)
    return MQTTClient

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

def read_sensor_data(mqttClient, sensor, pin, data_topic, iccid, random):
    '''Loop that send the data to AWS'''
    while True:
        # Send payload
        if random == 't':
            mqttClient.publish(data_topic, json.dumps(get_payload_random(iccid)), 0)
        else:
            mqttClient.publish(data_topic, json.dumps(get_payload(sensor, pin, iccid)), 0)
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
    sensor = sensor = Adafruit_DHT.DHT22
    pin = args.get('pin')
    iccid = args.get('iccid')
    clientId, endpoint, aws_root_cert, private_key, cert, data_topic = get_configurations()
    mqttClient = set_up_aws_connection(clientId, endpoint, aws_root_cert, private_key, cert)
    # Create connection to IoT Core
    mqttClient.connect()
    # Read sensor data and send it to aws
    read_sensor_data(mqttClient, sensor, pin, data_topic, iccid, args.random)
    # Disconnect
    mqttClient.disconnect()
