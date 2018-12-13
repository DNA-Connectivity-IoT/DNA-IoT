# DNA Control Center Azure connection

DNA offers connectivity for IoT devices to send data to cloud providers. DNA Control Center is tool that allows you to centrally manage your connectivity assets. Azure is major cloud provider that has many services, including ones that help build IoT connected devices. 

With the following instructions we connect a device to Azure cloud by utilizing DNA connectivity and integrate DNA Control Center generated statistics and connectivity status to Azure services. The instructions are built so that with little customization different sensors, gateways or DNA Control Center statistics (different with the ones in this demo) can be taken into action.

## Table of content
1. Azure setup
2. Gateway setup (Raspberry Pi)
3. Visualization
4. DNA Control Center

## Prerequisite 

In order to build demo for yourselves you need the following
- Azure Account
- Git
- Gateway device (in demo Raspberry pi 3 model B+ is used)
- DNA connectivity
- Basic knowledge of python
- Sensor is optional (in demo we used DHT22 temperature sensor)

## Azure Environment

### Create Resource group
```
az group create -l westeurope -n IoT-Resource-Group
```
### Create IoT hub
In iot-hub -folder fill in values for properties.json

Run this in Azure CLI 
```
az group deployment create 
--name iothubdeployment
--resource-group IoT-Resource-Group
--template-file template.json
--parameters @parameters.json
```
### Create Storage Account
In storage -folder fill in values for properties.json

Run this in Azure CLI
```
az group deployment create 
--name storagedeployment
--resource-group IoT-Resource-Group
--template-file template.json
--parameters @parameters.json
```
### Create Function App
In functions -folder fill in values for properties.json

Run this in Azure CLI
```
az group deployment create 
--name functionsdeployment
--resource-group IoT-Resource-Group
--template-file template.json
--parameters @parameters.json
```
## Register a thing

Run this in Azure CLI
```
az extension add --name azure-cli-iot-ext
az iot hub device-identity create --hub-name DNAControlCenterHub --device-id DnaRasp
```

Get the endpoint to where the data is send to 
```
az iot hub device-identity show-connection-string --hub-name DNAControlCenterHub --device-id DnaRasp --output table
```

You can then monitorin events coming to IoT Hub with running the following command in Azure Cli
```
az iot hub monitor-events --device-id DnaRasp --hub-name DNAControlCenterHub
```

## Raspberry Pi gateway

This demo assumes that you have set up the Raspberry Pi with the instructions found from Raspberry Pi webpage. 

Transfer the gateway folder to Raspberry Pi using scp.
``` 
scp /path/to/gateway pi@raspberrypi-local:~/gateway
```

> Raspberry Pi can run different OS, in this demo we use Raspbian. Regarding this demo, the OS should support running Python. Check that python is available and running version 2.7. If not, install python regarding your OS. `python --version`

Move the gateway folder to Raspberry Pi. Modify the config.ini file to match your IoT Hub endpoint.

Before we can run the sample code we need to install required libraries to python. You can do this with following commands. Requirements file is found under gateway folder. 
```
pip install virtualenv
python -m virtualenv -p python venv
source venv/bin/activate
pip install -r gateway/requirements.txt
```

Azure IoT Client also requires a libboost to be upgraded. Run the following command in Raspberry Pi to get it up to date
``` 
sudo apt-get install libboost-python1.62.0
```

Program has couple of parameters to help you get started. 

Parameter | Description | Values | Default
--- | --- | --- | ---
p | Pin number to which the sensor is attached | 2-26 | 2
r | Generate data. This can be used if no sensor is attached. Boolean type | t or f | f (false)
i | ICCID of the sim that is used for connectivity | 123456789 | 123456789
h | Help. |  | 

For example, if you want to run the program and send random generated data to AWS, run the following command
```
python mqtt_client.py -r t
```

You should now receive messages to Azure IoT Hub. You can visualize the data with time series insight.

> In this demo we pass the ICCID as parameter, since the Raspberry Pi is not set up to read connected SIM card ICCID. 

### Connect DHT22 sensor

In order to push real data, we need to connect sensor to the Raspberry Pi. We used DHT22 sensor that is simple temperature and humidity sensor. To get the IO pin information you can run ``` pinout ``` command in the terminal.

We need to connect the power to the 5v, ground to GND and IO pin to any of the GPIO pins. Just keep in mind witch pin you connected the sensor. When you run the program, pass the pin number as parameter (-p) and the program will read information from the sensor. 

For example, if the DHT22 is connected to pin number 2 and iccid of the sim is 76879096
``` 
python mqtt_client -p 2 -i 76879096
```
