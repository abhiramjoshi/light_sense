from gpiozero import DigitalInputDevice, DigitalOutputDevice
from time import sleep, time
import schedule
import light_sense, utils
import numpy as np
import pandas as pd
import model as md
from datetime import date, datetime, timedelta

#light_sensor = DigitalInputDevice(14)
control_pin = DigitalOutputDevice(15)
TOTAL_TIME = light_sense.TOTAL_TIME
TIME_DIV = light_sense.DIV_SIZE
START = 0
timezone = 0
START_TIME = START + timezone
END_TIME = START + TIME_DIV + 1
collected_data = light_sense.TimeSheet(div_size=TIME_DIV, total_time=TOTAL_TIME, start_time= START_TIME)
LEARNED_SCHEDULE = None #Dataframe


class EndSchedule(Exception):
    pass

def save_day_data(date):
    filename = f"./{date}_data.csv"
    collected_data.timesheet.to_csv(filename)

def record(schedule, time):
    print("Collecting data at time:", time)
    schedule.loc[time] = light_sensor.value
    print("Value collected is:", schedule.loc[time])

def control_lamp(time):
    if LEARNED_SCHEDULE is not None:
        if LEARNED_SCHEDULE[time] == 1:
            control_pin.on()
        else:
            control_pin.off()
    else:
        pass

def actions(timesheet, time):
    control_lamp(time)
    record(timesheet, time)

def end_schedule():
    raise EndSchedule

def create_schedule():
    global LEARNED_SCHEDULE
    LEARNED_SCHEDULE = md.predict_schedule((datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))

def data_management():
    global LEARNED_SCHEDULE
    light_sense.clear_data()
    light_sense.load_data()
    complete_data = light_sense.TimeSheet(timesheet = light_sense.complete_data)
    print("Compiling and saving data")
    save_day_data(collected_data.date.strftime('%Y-%m-%d'))
    light_sense.complete_data = light_sense.compile_data([complete_data, collected_data])
    light_sense.save_data()
    _,_ = modelling(light_sense.complete_data)
    LEARNED_SCHEDULE = create_schedule(light_sense.complete_data)

def new_day():
    global collected_data
    collected_data = light_sense.TimeSheet(div_size=TIME_DIV, total_time=TOTAL_TIME, start_time= START_TIME, date= date.today())
    print("The date is: ", collected_data.date)
    print(date.today())

def modelling(data):
    _, model = md.train_model(data)

def run(timesheet):
    # times = utils.create_time_index(TIME_DIV, TOTAL_TIME, start_time= START_TIME)
    # data = np.full(TOTAL_TIME//TIME_DIV, 0)
    times = timesheet.timesheet.index
    
    schedule.every().day.at("00:00").do(new_day)
    for time in times:
        schedule.every().day.at(time).do(actions, timesheet = timesheet.timesheet, time = time)
    schedule.every().day.at(utils.time_to_string(timesheet.end_time)).do(data_management)
    
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
    except (KeyboardInterrupt, EndSchedule):
        light_sensor.close()
        data_management()
        print(light_sense.complete_data)
        print("End")
        exit()
    

