/*
This code scans through DynamoDB
and returns first 100 items in http api
*/

const AWS = require('aws-sdk');

AWS.config.update({ region: "ap-northeast-2"});


exports.handler = async (event, context) => {
  const ddb = new AWS.DynamoDB({ apiVersion: "2012-10-08"});
  const documentClient = new AWS.DynamoDB.DocumentClient({ region: "ap-northeast-2"});
  
  // Scan through first 100 items in DynamoDB
  const params = {
    TableName: "ultrasonic",
    Limit: 100
  }
  
  //Return Items
  try {
    const response = await documentClient.scan(params).promise();
    const data = response.Items;
    return (data);
  } catch (err) {
    console.log(err);
  }
}
