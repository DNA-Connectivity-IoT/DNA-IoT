var ruuvi = require('node-ruuvitag')

var data = {};

var ruuvit = ['Ulkoruuvi', 'Alapohja1', 'Alapohja2']
var idt = ['e1c1a62d1d3c', 'e35f5b5fbc45', 'fc1bd191c0bc']
var data = {}
ruuvi.on('found', tag => {
    tag.on('updated', data1 => {
        var i = idt.indexOf(tag.id)
        if(i !== -1) data[ruuvit[i]] = data1
        else data[tag.id] =data1
    });
})

module.exports = {
    getdata: function () { return data }
}