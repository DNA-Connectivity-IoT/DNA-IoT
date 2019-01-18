# Integration of Cisco Jasper with IBM IoT Platform
<br>

## Overview

This repository contains an IoT demo for using Cisco Jasper with IBM Cloud. Cisco Jasper control centre is a platform for managing connectivity of IoT devices that use cellular network as data channel. IBM Cloud platform will be used to handle and visualise data flows and trigger event-based actions. This repository contains code and introductions for every component of the architecture that needs to be configured. This test platform was tested using jasper implementation from DNA. For the data communication we used DNA starter kit which provided required SIM cards for the IOT solution.
<br><br>

![architecture](https://raw.githubusercontent.com/mikkopitkaenen/ibm-cloud-with-cisco-jasper/master/readme_images/architecture.png)<br>
**Architecture of the solution**

1. Network of devices. Gateway sends data on behalf of other devices and sensors. In this demo Node-RED will be used as logic application, Raspberry Pi as the gateway device and TI SensorTag as data-sending sensor. One sensor has dashed line because gateway device auto-registers devices/sensors and adding another sensor device wouldn't require any actions.
2. Company-specific private APN is gateway between networks.    
3. Data is sent from devices to IBM Cloud via MQTT Protocol.
4. Edge services are needed to allow data to flow safely over the Internet.
5. Watson IoT Platform is MQTT Broker that receives IoT Data and publishes it for subscribed applications. It is possible to create triggers for payload events.
6. Coordination of workflow logic. In this demo Node-RED will be used to handle logic.
7. Jasper is a platform for managing IoT Devices that access internet via cellular data network. It is possible to create triggers for management events.
8. Event ‘Device Registration’: When SIM-card is inserted into a device, the device will be auto-registered in Watson IoT Platform.
9. Event ‘SIM Alert’: When SIM-card is inserted into a new device event will be triggered.
10. Event ‘Sensor Data Alert’: When pre-defined device data exceeds certain threshold, event will be triggered.

If there was a private APN, it would be possible to isolate the devices to a secure private network. With this connecting a new gateways can be easily auto-registered. Basically it means adding a new devices to environment would not require any configuration concerning connectivity. This will streamline the provisioning process including exchange of Watson IoT API key exchange.

## Prerequisites
- [Free IBM Cloud Account](https://bluemix.net/)
- [Jasper Control Centre account](https://dna.jasper.com) and M2M SIM card *
- Raspberry Pi
- TI SensorTag

*\*This demo can be done with a SIM card with no remaining data (in case of free starter kit). Internet connection can be created via Wi-Fi. Jasper Control Centre will not show information about data usage but event triggers will work normally.*


## Contents<br>
1. IBM Cloud application configuration<br>
2. IoT gateway device application configuration<br>
3. Watson IoT Platform configuration <br>


#### Part 1: IBM Cloud application configuration
Click the link below to deploy needed components to IBM Cloud. Clicking the deploy button will create Node-RED and Watson IoT Platform instances in your personal account. <br>
[![Deploy to Bluemix](https://bluemix.net/deploy/button.png)](https://bluemix.net/deploy?repository=https://github.com/mikkopitkaenen/test.git&branch=master)

Node-RED instance created by the link will contain custom flow. If you already have a Node-RED application in IBM Cloud, you can import the code manually from /defaults/flow.json


Devices do not have to be entered manually in IBM IoT Platform because Jasper will detect SIM Card insertion and send message to application endpoint. If SIM card will be changed to a new device with a new IMEI, alert will be posted to cloud application endpoint. These triggers have to be configured in Jasper Control Centre.

Endpoint addresses are needed in order to use Jasper rules.
Launch Node-RED. On the first tab 'Rules' there are three endpoints. Two of them are '\_jasper' annotated that means they are Jasper platform triggered events, and created in Jasper platform. The third one is for IBM IoT Platform triggered rule, and created in IBM IoT platform.
In this step it is necessary to log into IBM IoT platform in order to find out organisation identifier.
Step-by-step information is inside Node-RED comment nodes in 'Rules' tab.


#### Part 2: IoT device application configuration
In this part Raspberry Pi will be configured to send and receive data. Node-RED will be the application to handle logic. If you do not have Node-RED installed on your Raspberry Pi install it [here](https://nodered.org/docs/getting-started/installation).
<br>
To create Node-RED flow and required modules to your Raspberry Pi, run the command below in the terminal of your device

```
wget -O - https://raw.githubusercontent.com/mikkopitkaenen/test/master/gateway/.script.sh | sh
```

Sensor network will consist of one gateway device (Raspberry Pi) and one sensor device (TI SensorTag). Gateway devices can send data on behalf of other devices. Devices connected to gateway device will also be auto-registered in IBM IoT device.

You can monitor flow of data in Node-RED dashboard UI in URL 'http://{local_ip}:1880/ui'. This dashboard is accessible only locally on the gateway device.
To check whether data has been successfully sent to IBM Cloud, you can open dashboard in URL 'https://{yourdomain}.mybluemix.net/ui'

#### Part 3: Watson IoT Platform configuration
In this part cloud a rule for sensor payload will be created. In order to create cloud rules, schema is required to be defined. You must create a schema to map device properties to user-friendly properties names, set the data units for the properties, and specify a message type to use with the schema. In part 2 sensor data was sent to IBM IoT platform. This makes defining schema easier as data properties and types will be autofilled.<br>
Step-by-step information is inside Node-RED comment node in 'Rules' tab.
