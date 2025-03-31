const express = require('express')
const app = express()
var port = 4000

var mongojs = require('mongojs')
var Promise = require('promise')
var myiotdb = mongojs('mongodb://127.0.0.1:27017/bananaproject');
var devid, uuid,idesp, datasize, dataset=''



app.get('/', function (req, res) {
  res.send("My IOT Protocol ready !")
})

app.get('/write/:uuid/:idesp', function (req, res) {
  var strParseWriteReq = JSON.stringify(req.params)
  var strWriteReq = JSON.parse(strParseWriteReq)
  uuid = strWriteReq.uuid
  idesp = strWriteReq.idesp
  writedata(uuid,idesp, res)
})

app.get('/read/:datasize', function (req, res) {
  var strParseReadReq = JSON.stringify(req.params)
  var strReadReq = JSON.parse(strParseReadReq)
  datasize = strReadReq.datasize
  readdata(datasize, res)
})


app.listen(port, function () {
  var nodeStartTime = new Date()

  console.log('My IoT protocol running on port ' + port + ' start at ' + nodeStartTime.toLocaleString("th-TH", { timeZone: "Asia/Bangkok" }))
})

/* -- ASYNC / AWAIT function -- */

async function writedata(_uuid, _idesp, res){
  await writeDataToMongo(_uuid, _idesp, res)
}

function writeDataToMongo(_saveuuid, _saveidesp, res) {
    return new Promise(function(resolve, reject) {
        var mywritecollection = myiotdb.collection('dataTest');

        mywritecollection.insertOne({
            uuid: _saveuuid,
            idesp: _saveidesp,
            timestamp: new Date().toLocaleString("th-TH", { timeZone: "Asia/Bangkok" }),
        }, function(err, result) {
            if (err) {
                console.log(err);
                res.send(String(err));
            } else {
                console.log('Record data ok');
                res.send('Record data ok');
            }
        });
    });
}
  

async function readdata(_datasize, res){
  await readDataFromMongo(_datasize, res)
}

function readDataFromMongo(_readdatasize, res){
  return new Promise(function(resolve,reject){
    var myreadcollection = myiotdb.collection('dataTest')
    myreadcollection.find({}).limit(Number(_readdatasize)).sort({recordTime: -1}, function(err, docs){
      //console.log(JSON.stringify(docs))
      res.jsonp(docs)
    })
  })
}

