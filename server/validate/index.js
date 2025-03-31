const express = require('express');
const app = express();
const port = 4000;
const { MongoClient } = require('mongodb');
const uri = 'mongodb://127.0.0.1:27017';
//1 รอบ 2 อุปกรณ์ 1 อุปกรณ์ต้องส่งแค่ 1 ครั้ง ทำเช็คข้อมูลถ้ามีข้อมูลแล้วเข้าซ้ำจะไม่เข้า database ถ้าเริ่มรอบใหม่จะรับข้อมูลอุปกรณ์ 1 ได้ buffer
//เพิ่ม state inprocess finish
app.use(express.json());

app.get('/', (req, res) => {
  res.send('My IOT Protocol ready !');
});

const listround = [];
const weightround = [];
app.post('/writeuuid/:uuid/:idesp', async (req, res) => {
  const uuid = req.params.uuid;
  const idesp = req.params.idesp;
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const existingData = await client
      .db('bananaproject')
      .collection('dataTest')
      .findOne({ uuid: uuid, idesp: idesp ,state: 'In Process'});
      
    const sendWeight = await client
      .db('bananaproject')
      .collection('dataTest')
      .findOne({ uuid: uuid ,state: 'In Process'});

    if (existingData) {
      await client
        .db('bananaproject')
        .collection('dataTest')
        .updateOne(
          { uuid: uuid, idesp: idesp, state: 'In Process'},
          { $set: { state: 'Finish' } }
          
        );
        listround.push(uuid);
        console.log(listround);
      console.log('UUID ' + uuid + ' and IDESP ' + idesp + ' สถานะ Finish');

      const existingDataWeight = await client
      .db('bananaproject')
      .collection('dataTest')
      .findOne({state: 'In Process' , uuid: uuid });

      if (existingDataWeight) {
        await client
          .db('bananaproject')
          .collection('dataTest')
          .updateOne(
            {state: 'In Process' , uuid: uuid},
            { $set: { state: 'Finish' } }
          );
          if (sendWeight) {
            const w = sendWeight.weight;
            const grade = 'A'
            await client.db('bananaproject').collection('result').insertOne({
              grade: grade,
              weight: w,
              state: 'Finish',
              timestamp: new Date().toLocaleString('th-TH', { timeZone: 'Asia/Bangkok' }),
            });
            await client
            .db('bananaproject')
            .collection('dataTest')
            .deleteMany({ state: 'Finish', uuid: uuid });
            console.log('เพื่มน้ำหนักกล้วย ' + sendWeight.weight + ' ลง result');
          }
          console.log('กล้วย ' + ' สถานะ Finish');
      }
    }
    
    if (listround.includes(uuid)){
      if (listround.length === 2) {
        listround.splice(0, listround.length);
        console.log('Listround ครบ 2 ตัว ทำการลบทั้งหมด');
      }
    } else {
      await client
      .db('bananaproject')
      .collection('result')
      .deleteMany({ state: 'Finish'});
      await client.db('bananaproject').collection('dataTest').insertOne({
        uuid: uuid,
        idesp: idesp,
        timestamp: new Date().toLocaleString('th-TH', { timeZone: 'Asia/Bangkok' }),
        state: 'In Process',
      });

      console.log('UUID ' + uuid + ' and ID ' + idesp + ' เพิ่มลง Database');
    }

    res.status(200).send({});
  } finally {
    await client.close();
  }
});

app.get('/read', async (req, res) => {
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const data = await client.db('bananaproject').collection('result').find({}).toArray();
    res.status(200).send(data);
  } finally {
    await client.close();
  }
});

app.post('/writeweight/:weight/:uuid', async(req, res) => {
  const weight = req.params.weight;
  const uuid = req.params.uuid;
  const client = new MongoClient(uri);
  await client.connect();
  const existingData = await client
    .db('bananaproject')
    .collection('dataTest')
    .findOne({ uuid: uuid,state: 'In Process'});
        if (listround.includes(uuid)){
          if (weightround.length === 2) {
            weightround.splice(0, weightround.length);
            console.log('weightround ครบ 2 ตัว ทำการลบทั้งหมด');
          }
        }
      else{
        if (!existingData && !weightround.includes(uuid)){
          await client.db('bananaproject').collection('dataTest').insertOne({
            weight: weight,
            uuid: uuid,
            state: 'In Process',
            timestamp: new Date().toLocaleString("th-TH", { timeZone: "Asia/Bangkok" }),
            
          });
          weightround.push(uuid);
          console.log('Record data ok');
        }
      }
  await client.close();
  res.status(200).send({
      
  });
})
/*app.get('/readweight', async(req, res) => {
  const weight = req.params.weight;
  const idesp = req.params.idesp;
const state = req.params.state;
  const client = new MongoClient(uri);
  await client.connect();
  await client.db('banana').collection('banana').insertOne({
    weight: weight,
    idesp: idesp,
    state: state,
    timestamp: new Date().toLocaleString("th-TH", { timeZone: "Asia/Bangkok" }),
  });
  await client.close();
  console.log('Record data ok');
  res.status(200).send({
      
  });
})*/

app.listen(port, () => {
  console.log(
    'My IoT protocol running on port ' +
      port +
      ' start at time ' +
      new Date().toLocaleString('th-TH', { timeZone: 'Asia/Bangkok' })
  );
});
