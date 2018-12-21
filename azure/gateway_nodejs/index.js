'use strict';

var Client = require('azure-iot-device').Client;
var Protocol = require('azure-iot-device-mqtt').Mqtt;
var Message = require('azure-iot-device').Message;
var _ = require('lodash');

var connectionString = '<IoT hub connection string>';

var client = Client.fromConnectionString(connectionString, Protocol);

client.open(function (err) {
    if (err) {
        console.error('could not open IotHub client');
    }
    else {
        console.log('client opened');
        // Create device Twin
        client.getTwin(function (err, twin) {
            if (err) {
                console.error('could not get twin');
            }
            else {
                console.log('twin created');
                var iccid = "";
                twin.on('properties.desired', function (delta) {
                    console.log('new desired properties received:');
                    console.log(JSON.stringify(delta.ICCID));
                });

                twin.on('properties.desired', function (delta) {
                    var patch = {
                        ICCID: delta.ICCID,
                        DataUsage: delta.DataUsage
                    }
                    twin.properties.reported.update(patch, function (err) {
                        if (err) console.log(err)
                        else console.log('twin state reported')
                    })
                });
                client.on('message', function (msg) {
                    console.log('Id: ' + msg.messageId + ' Body: ' + msg.data);
                    client.complete(msg, printResultFor('completed'));
                });

                // Create a message and send it to the IoT Hub every two seconds
                // Implement sensor reading code here
                var sendInterval = setInterval(function () {
                    console.log(twin.properties)
                    var iccid = twin.properties.reported.ICCID
                    var dataUsage = twin.properties.reported.DataUsage
                    var windSpeed = 10 + (Math.random() * 4); // range: [10, 14]
                    var temperature = 20 + (Math.random() * 10); // range: [20, 30]
                    var humidity = 60 + (Math.random() * 20); // range: [60, 80]
                    var data = { deviceId: 'myFirstDevice', windSpeed: windSpeed, temperature: temperature, humidity: humidity, iccid: iccid, dataUsage: dataUsage };
                    var message = new Message(JSON.stringify(data));
                    console.log('Sending message: ' + message.getData());
                    client.sendEvent(message, printResultFor('send'));
                }, 2000);

                client.on('error', function (err) {
                    console.error(err.message);
                });

                client.on('disconnect', function () {
                    clearInterval(sendInterval);
                    client.removeAllListeners();
                    client.open(connectCallback);
                });


            }
        });
    }


});

function printResultFor(op) {
    return function printResult(err, res) {
        if (err) console.log(op + ' error: ' + err.toString());
        if (res) console.log(op + ' status: ' + res.constructor.name);
    };
}