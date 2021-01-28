import os
import sys
import datetime
import time
import picamera
try:
    import boto3
    import threading
    import RPi.GPIO as GPIO
    print("All Modules Loaded ......")
except Exception as e:
    print("Error {}".format(e))

"""
Global variable
"""
distance = 0
sensor_id = 0
date = ' '
now = ' '
img = ' '

class MyDb(object):
    def __init__(self, Table_Name='ultrasonic'):
        self.Table_Name=Table_Name
        
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(Table_Name)
        
        self.client = boto3.client('dynamodb')
        
    @property
    def get(self):
        response = self.table.get_item(
            key={
                'sensor_id':"1"
            }
        )
        
        return response
    
    def put(self, sensor_id='' , name='', distance=''):
        global date, now
        date = time.strftime("%Y%m%d")
        now = time.strftime("%H%M%S")
        self.table.put_item(
            Item={
                'sensor_id':sensor_id,
                'name': name,
                'distance' : distance,
                'date' : date,
                'time' : now,
                'isnearby' : MyDb.isnearby()
            }
        )
        

    def delete(self,Sensor_Id=''):
        self.table.delete_item(
            key={
                'Sensor_Id': Sensor_ID
            }
        )
    
    def describe_table(self):
        response = self.client.describe_table(
            TableName='Sensor'
        )
        return response
    
    @staticmethod
    def isnearby():
        if distance < 100:
            return True
        else:
            return False
    
    @staticmethod
    def distcheck():
        global distance
        
        GPIO.setmode(GPIO.BCM)
        
        TRIG = 23
        ECHO = 24
        
        GPIO.setup(TRIG,GPIO.OUT)
        GPIO.setup(ECHO,GPIO.IN)

        GPIO.output(TRIG, False)
        print ("Waiting For Sensor To Settle")
        time.sleep(2)

        GPIO.output(TRIG,True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO)==0:
            pulse_start = time.time()

        while GPIO.input(ECHO)==1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * 17150

        distance = round(distance, 2)
        
        if distance is not None:
            print('Distance is %d cm' % distance)
        else:
            print('Failed to get reading.')
        GPIO.cleanup()
        return int(distance)
    
    @staticmethod
    def measure_average():
        global distance
        # This function takes 3 measurements and
        # returns the average.
        distance1 = MyDb.distcheck()
        time.sleep(0.3)
        distance2 = MyDb.distcheck()
        time.sleep(0.3)
        distance3 = MyDb.distcheck()
        distance = distance1 + distance2 + distance3
        distance = distance / 3
        return int(distance)

    def capture_image():
        #Create image name
        global img, date, now
        z = date + "-" + now
        img = 'img' + z + '.jpg'
        #capture image
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.start_preview()
            camera.capture(img)
            camera.stop_preview()
            camera.close()
            return

    def upload_image():
        global img
        s3 =boto3.client('s3')
        filename = img
        filename_local = '/home/pi/python/'+ filename
        bucket_name = 'visitorimage'
        s3.upload_file(filename, bucket_name, filename)

def main():
    global sensor_id
    threading.Timer(interval=10, function=main).start()
    dynamo = MyDb()
    distance = dynamo.measure_average()
    dynamo.put(sensor_id= str(sensor_id), name = "Guest", distance = distance)
    if dynamo.isnearby() is True:
        MyDb.capture_image()
        time.sleep(0.3)
        print('Captured')
        MyDb.upload_image()
        time.sleep(2)
    print ("uploaded sensor_id %s" %sensor_id)
    sensor_id += 1
    
if __name__ == "__main__":
    main()
