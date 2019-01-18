
var Registry = require('azure-iothub').Registry;
var crypto = require('crypto-js')
var parser = require('xml2js').parseString

function parseMessage(msg) {
    var data = {}
    decodeURIComponent(msg).split('&').forEach(kvp => {
        data[kvp.substring(0, kvp.indexOf('='))] = kvp.substring(kvp.indexOf('=') + 1, kvp.length)
    })
    parser(data.data.replace(/\+/gi, ' '), (err, result) => {
        if (err) {
            console.log(err)
        }
        else {
            data.properties = {};
            if (result.NoConnection) {
                data['iccid'] = result.NoConnection.iccid[0]
                data.properties['noConnectionTime'] = data.timestamp
            }
            if (result.Past24HDataUsage) {
                data['iccid'] = result.Past24HDataUsage.iccid[0]
                data.properties['dataUsage'] = result.Past24HDataUsage.dataUsage[0]
                data.properties['dataUsageTime'] = data.timestamp
            }
        }
    })
    return data;
}

function checkApiKey(timestamp, apikey, signature) {
    return crypto.enc.Base64.stringify(crypto.HmacSHA1(timestamp, apikey)) === signature
}

async function getTwin(iccid, registry) {
    return new Promise(function (resolve, reject) {
        var query = registry.createQuery('SELECT * FROM devices WHERE tags.ICCID =\'' + iccid + '\'', 100);
        //query device registry with iccid in tags
        query.nextAsTwin(null, function (err, results) {
            if (err) {
                reject(err)
            } else {
                var deviceId;
                results.forEach(function (twin) {
                    deviceId = twin.deviceId
                });
                if (!deviceId) {
                    reject({ message: 'no deviceid found' })
                }
                else {
                    resolve(deviceId)
                }
            }
        })
    });
};

async function updateTwin(registry, deviceId, desired) {
    console.log(deviceId)
    console.log(desired)
    return new Promise((resolve, reject) => {
        registry.getTwin(deviceId, function (err, twin) {
            if (err) {
                reject(err)
            }
            else {
                //create pathc for updated properties
                var twinPatch = {
                    properties: {
                        desired
                    }
                };

                // update twin properties
                twin.update(twinPatch, function (err, twin) {
                    if (err) {
                        reject(err);
                    } else {
                        registry.updateTwin(twin.deviceId, twinPatch, twin.etag, function (err, twin) {
                            if (err) {
                                reject(err);
                            } else {
                                resolve(JSON.stringify(twin, null, 2));
                            }
                        });
                    }
                });
            }
        })
    });
}

module.exports = async function (context, req) {
    context.log('JavaScript HTTP trigger function processed a request.');
    var apikey = process.env['apikey'];
    //parse request body
    var data = parseMessage(req.body);
    //check api key validity
    if (!checkApiKey(data.timestamp, apikey, data.signature)) { 
        context.res = {
            status: 403,
        }
        return;
    }

    try {
        var registry = Registry.fromConnectionString(process.env['IoTHubConnection'])
        var deviceId = await getTwin(data.iccid, registry, context)
        await updateTwin(registry, deviceId, data.properties)
        context.res = {
            status: 200
        }
    } catch (error) {
        context.res = {
            status: 403,
        }
    }
};
