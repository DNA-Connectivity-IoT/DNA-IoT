var Registry = require('azure-iothub').Registry;

async function getTwin(iccid, registry ) {
    return new Promise(function (resolve, reject) {
        var query = registry.createQuery('SELECT * FROM devices WHERE tags.ICCID =\'' + iccid + '\'', 100);
        //query device registry with iccid in tags
        query.nextAsTwin(null, function (err, results) {
            if (err) {
                reject(err)
            }  else {
                var deviceId;
                results.forEach(function (twin) {
                    deviceId = twin.deviceId
                });
                if(!deviceId){
                    reject({ message: 'no deviceid found'})
                }
                else{
                    resolve(deviceId)
                }
            }
        })
    });
};

async function updateTwin(registry, deviceId, desired, context) {
    return new Promise((resolve, reject) => {
        registry.getTwin(deviceId, function (err, twin) {
            if (err) {
                reject(err)
            } 
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
        })
    });
}

module.exports = async function (context, req) {
    context.log('JavaScript HTTP trigger function processed a request.');
    //set request body to desired properties
    var desired = req.body ? req.body : {}
    var iccid = '';
    //take ICCID from body and remove it from properties
    if (desired.ICCID) {
        iccid = desired.ICCID;
        delete desired.ICCID;
    }
    
    var registry = Registry.fromConnectionString('<IoTHub connection string>')

    try {
        var deviceId = await getTwin(iccid, registry, context)
        var updated = await updateTwin(registry, deviceId, desired, context)
        context.res = {
            body:updated
        }
    } catch (error) {
        context.res = {
            status: 500,
            body: error.message
        }
    }
};