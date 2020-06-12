from gpiozero import DigitalInputDevice
from time import sleep, time
import schedule
import light_sense, utils

light_sensor = DigitalInputDevice(14)

def record(schedule, time):
    schedule[time]

def loop():
    while True:
        print(light_sensor.value)
        if light_sensor.value == 1:
            print("light is on")
        else:
            print("light is off")
        sleep(1)

if __name__ == "__main__":
    test_day = light_sense.TimeSheet()
    try:
        loop()
    except KeyboardInterrupt:
        light_sensor.close()
        print("End")
        exit()
    

