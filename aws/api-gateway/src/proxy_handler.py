import urllib
import xmltodict
import hmac
import hashlib
import base64
import logging
import boto3
import datetime
import os
from botocore.exceptions import ClientError

# Configuring logger
logger = logging.getLogger()
# set logger level (levels: DEBUG, INFO, WARNING, ERROR, CRITICAL)
logger.setLevel(logging.DEBUG)

METRIC_NAME = 'DnaControlCenterMetrics'


def request_proxy(data):
    '''Parse data from the XML body'''
    payload = urllib.unquote(urllib.unquote(data['body']))
    data = {}
    for row in payload.split('&'):
        data[(row.split('='))[0]] = row[len(row.split('=')[0])+1:]
    headers = data
    data['data'] = data['data'].replace('+', ' ')
    data = dict(xmltodict.parse(data['data']))
    data[data.keys()[0]] = dict(data[data.keys()[0]])
    return data, headers


def request_parameters(data):
    '''Get info from AWS proxy'''
    path = data['path']
    return path


def check_api_key(timestamp, signature):
    '''Check that send message API is correct
    API_SECRET_KEY is set in the jasper console'''
    dig = hmac.new(os.environ['api_key'], msg=timestamp.encode(), digestmod=hashlib.sha1).digest()
    hashed = base64.b64encode(dig).decode()
    return hashed == signature


def response(status):
    '''Generate response message'''
    response = {"statusCode": status}
    return response


def put_no_connection_metric(data, datestamp):
    client = boto3.client('cloudwatch')
    logger.debug('writing no connection data to cloudwatch')
    try:
        response = client.put_metric_data(
            Namespace=METRIC_NAME,
            MetricData=[
                {
                    'MetricName': 'NoConnection',
                    'Dimensions': [
                        {
                            'Name': 'ICCID',
                            'Value': (data['NoConnection']['iccid'])
                        },
                    ],
                    'Timestamp': datestamp,
                    'Value': 1,
                    'StorageResolution': 60
                },
            ]
        )
    except ClientError as e:
        logger.error(e.response['Error']['Message'])


def put_data_usage_metric(data, datestamp):
    logger.debug('writing data usage info to cloudwatch')
    client = boto3.client('cloudwatch')
    try:
        response = client.put_metric_data(
            Namespace=METRIC_NAME,
            MetricData=[
                {
                    'MetricName': 'DataUsage',
                    'Dimensions': [
                        {
                            'Name': 'ICCID',
                            'Value': (data['Past24HDataUsage']['iccid'])
                        },
                    ],
                    'Timestamp': datestamp,
                    'Value': int(data['Past24HDataUsage']['dataUsage']),
                    'Unit': 'Bytes',
                    'StorageResolution': 60
                },
            ]
        )
    except ClientError as e:
        logger.error(e.response['Error']['Message'])


def put_metrics(path, data, timestamp):
    datestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    if path == '/NoConnection':
        put_no_connection_metric(data, datestamp)
    elif path == '/DataUsage':
        put_data_usage_metric(data, datestamp)


def handler(event, context):
    '''Main function for the lambda'''
    logger.debug(event)
    path = request_parameters(event)
    data, headers = request_proxy(event)

    # Check api key is ok
    if not check_api_key(headers['timestamp'], headers['signature']):
        logger.error("ERROR, API KEY DOES NOT MATCH")
        return(response(403))
    else:
        logger.debug("API KEY OK")

    put_metrics(path, data, headers['timestamp'])
    return response(200)
