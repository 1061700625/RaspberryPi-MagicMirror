import Adafruit_DHT
import RPi.GPIO as GPIO

def updateTempHum():
    sensor = Adafruit_DHT.DHT11
    gpio = 4
    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio, retries=2)
    if humidity:
        humidity = str(humidity) + '%'
        print(humidity)
    if temperature:
        temperature = str(temperature) + '°'
        print(temperature)


import adafruit_dht

def updateTempHum2():
    GPIO.cleanup()
    dhtDevice = adafruit_dht.DHT11(4)
    temperature_c = dhtDevice.temperature
    temperature_f = temperature_c * (9 / 5) + 32
    humidity = dhtDevice.humidity
    print(
        "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
            temperature_f, temperature_c, humidity
        )
    )
    dhtDevice.exit()
    

import subprocess
import json
def updateTempHum3():
    res = json.loads(subprocess.check_output('./dht11', timeout=5).decode('utf-8'))
    print(res)
    print(res['RH'])
    print(res['TMP'])



updateTempHum3()





