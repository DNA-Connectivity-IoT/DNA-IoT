var ruuvi = require('node-ruuvitag')

var data = {};

var ruuvit = ['ruuvi1', 'ruuvi2', 'ruuvi3']
var idt = ['<ruuvi1_tag.id>', '<ruuvi2_tag.id>', '<ruuvi3_tag.id>']
var data = {}
ruuvi.on('found', tag => {
    tag.on('updated', data1 => {
        var i = idt.indexOf(tag.id)
        if (i !== -1) data[ruuvit[i]] = data1
        else data[tag.id] = data1
    });
})

module.exports = {
    getdata: function () { return data }
}