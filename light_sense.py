import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
import random
import utils as u

FACTORS = list(u.factors(1440))
filename = './complete_data.csv'
learned_data = './learned_data.csv'
complete_data = pd.DataFrame()
GAMMA = 0.5
threshold = 1
learned_schedule = pd.DataFrame()

#Load and save data to and from csv
def save_data():
    complete_data.to_csv(filename)

def load_data():
    complete_data = pd.read_csv(filename)

def clear_data():
    complete_data = pd.DataFrame()

def save_learned_data():
    learned_schedule.to_csv(learned_data)

def load_learned_data():
    learned_schedule = pd.read_csv(learned_data)

def clear_learned():
    warning = input("This will clear all learned schedules from memory, do you wish to continue? \n [Y/n]")
    if warning is 'Y' or warning is 'y':
        learned_data = pd.DataFrame()
        save_learned_data()

"""
What does our program need to do? First we need to load our data and save our data into a writable file. This will probably be a set of tuples therefore a text/csv file will probably work well

Next, the idea of the program will be to return a schedule of light on off times based on when the light has been turned on previously. This means that that we need to be able to make a 'timesheet' for each day indicated when the light was on and off. This data will then be incorporated into the learning to help develop a schedule for the next day for when the light needs to be on and off. Finally we will need to find a way of intellegently 'learning' so that we can make intellegent schedulings for when we want the light to be on and when we want the light to be off
"""

class TimeSheet:
    def __init__(self, date = datetime.now(), data = None, div_size = 10):
        """
        Inputs
        ------
        div_size: The size of the time divisions of a particular day in minutes. A div_size that doesnt break down the day into whole number minute divisions is rounded to the nearest div_size that accomplishes this
        data: The on/off light data that will be given by the microcontroller, 'random' for randome data, 'ones' for ones, deafult is zeros
        date: the date of the data
        """

        self.date = date
        self.div_size = u.get_whole_div(div_size, FACTORS)
        if data is 'random':
            data = u.random_data(self.div_size)
        if data is 'ones':
            data = np.full(1440//self.div_size, 1)
        self.timesheet = u.construct_dataframe(data, self.div_size, self.date.strftime('%Y-%m-%d'))

    def __str__(self):
        return self.timesheet.to_string()

    def fill(self, num_div, new_index):
        new_index_df = pd.DataFrame(index=new_index)
        self.timesheet = pd.concat([new_index_df,self.timesheet], axis = 1)
        for i,row in enumerate(new_index):
            if i is not 0:
                if pd.isnull(self.timesheet.loc[row][0]):
                    if self.timesheet.iloc[i-1][0] == 1:
                        self.timesheet.loc[row][0] = 1
                    else:
                        self.timesheet.loc[row][0] = 0

def compile_data(day_data):
    """
    Compiles all the data from multiple days into one dataframe
    day_data: list of TimeSheet objects
    """
    # def get_max_index(day_data):
    #     lengths = [day.timesheet.size for day in day_data]
    #     max_day = lengths.index(max(lengths))
    #     max_data_index = day_data[max_day].timesheet.index
    #     return max_data_index 
    # max_index = get_max_index(day_data)

    complete_index = pd.DataFrame(index = day_data[0].timesheet.index)
    for day in day_data:
        day_index = pd.DataFrame(0, columns = ['remove'], index = day.timesheet.index)
        complete_index = pd.concat([complete_index,day_index], axis = 1, sort = True)
        complete_index = complete_index.drop(['remove'], axis=1)
    
    complete_df = pd.DataFrame(index = complete_index.index)
    for day in day_data:
        day.fill(complete_df.index.size, complete_df.index)
        complete_df = pd.concat([complete_df,day.timesheet], axis = 1, sort = True)
    return complete_df

def calculate_duaration(schedule):
    """
    Calculates the duration the light has been on for. This is an extra feature that is intended to be used for machine learning purposes

    Input
    ------
    schedule: The daily timesheet 

    Returns
    -------
    Timesheet with duration column added and last duration column value
    """
    schedule_copy = schedule.copy()
    schedule_length = (len(schedule_copy["learned schedule"].index)-1)
    if "duration" in schedule_copy.columns:
        pass
    else:
        schedule_copy["duration"] = ""
        for i, time in enumerate(schedule_copy["learned schedule"].index):
            if schedule_copy['learned schedule'][i] == 1:
                if i == 0:
                    try:
                        schedule_copy['duration'][i] = schedule_copy['last duration'][0]
                    except KeyError:
                        schedule_copy['duration'][i] = 0
                else:
                    schedule_copy['duration'][i] = schedule_copy['learned schedule'][i] + schedule_copy['duration'][(i-1)]
            else:
                schedule_copy['duration'][i] = 0    
            if i == schedule_length:
                schedule_copy['last duration'] = ''
                schedule_copy['last duration'][0] = schedule_copy['duration'][i]
    return schedule_copy


def calculate_timesegement(time_data):
    """
    Calculates the value of the state of the light at each time given previous data points.

    Input
    -----
    Time_data: Row of datapoints indication if the light has been on or off on previous days for one particular time segement

    Returns
    -------
    Predicted state of the light for future day.
    """
    prev_sum = 0
    for t in time_data:
        if pd.isnull(t):
            pass
        else:
            prev_sum = t + (GAMMA*prev_sum)
    if prev_sum > threshold:
        return 1
    else:
        return 0

def calculate_schedule(complete_data):
    """
    Calculates a complete schedule using predicted values for when the lamp should be on

    Input
    -----
    complete_data: copleted timesheets

    Returns
    -------
    Shedule of predicted light state values
    """
    results = []
    for row in complete_data.index:
        result = calculate_timesegement(complete_data.loc[row, :])
        results.append(result)
    schedule = pd.DataFrame(results, index=complete_data.index, columns=['learned schedule'])
    return schedule

def run(day_data):
    """
    Completes the data, calulates schedule, adds feature to schedule
    """
    complete_data = compile_data(day_data)
    schedule = calculate_schedule(complete_data)
    schedule = calculate_duaration(schedule)
    return schedule, complete_data

#Fill out daily timesheet indicating when the light was on and off

#Learn when the light needs to be on and off for the next day

#Create a schedule for the next day that can be sent to a microcontroller 

#Write code for the microcontroller to first detect the light and then also control the light based on the schedule that we create for it.

if __name__ == "__main__":
    

    day1 = TimeSheet(div_size=39)
    day2 = TimeSheet()
    day3 = TimeSheet(date=datetime.now() + timedelta(days=random.randint(0,20)), data='random', div_size=20)
    day4 = TimeSheet(date=datetime.now() + timedelta(days=20), data='ones', div_size=25)
    complete_data = compile_data([day1, day2, day3, day4])
    save_data()
    clear_data()
    load_data()
    print(complete_data)
    print(calculate_schedule(complete_data))
    complete_data = compile_data([day1, day2, day3, day4])
    print(complete_data)