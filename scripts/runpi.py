from gpiozero import DigitalInputDevice
from time import sleep, time
import schedule
import light_sense, utils
import numpy as np
import pandas as pd

#light_sensor = DigitalInputDevice(14)
TOTAL_TIME = 1440
TIME_DIV = 10
START = 0
timezone = 0
START_TIME = START + timezone
END_TIME = START + TIME_DIV + 1
collected_data = light_sense.TimeSheet(div_size=TIME_DIV, total_time=TOTAL_TIME, start_time= START_TIME)

class EndSchedule(Exception):
    pass

def record(schedule, time):
    print("Collecting data at time:", time)
    schedule.loc[time] = light_sensor.value

def end_schedule():
    raise EndSchedule

def data_management():
    light_sense.clear_data()
    light_sense.load_data()
    complete_data = light_sense.TimeSheet(timesheet = light_sense.complete_data)
    print(type(complete_data))
    light_sense.complete_data = light_sense.compile_data([complete_data, collected_data])
    light_sense.save_data()

def run(timesheet):
    # times = utils.create_time_index(TIME_DIV, TOTAL_TIME, start_time= START_TIME)
    # data = np.full(TOTAL_TIME//TIME_DIV, 0)
    times = timesheet.timesheet.index
    
    for time in times:
        schedule.every().day.at(time).do(record, schedule = timesheet.timesheet, time = time)
    schedule.every().day.at(utils.time_to_string(timesheet.end_time)).do(end_schedule)
    
    while True:
        schedule.run_pending()

def loop():
    while True:
        print(light_sensor.value)
        if light_sensor.value == 1:
            print("light is on")
        else:
            print("light is off")
        sleep(1)

if __name__ == "__main__":
    print(collected_data)
    try:
        run(collected_data)
    except EndSchedule:
        light_sensor.close()
        data_management()
        print(light_sense.complete_data)
        print("End")
        exit()
    

