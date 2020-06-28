import numpy as np
import pandas as pd
from datetime import datetime

class IndexSpanError(Exception):
    pass

def factors(n):
    """
    Returns all factors of n in list
    """
    return set(x for tup in ([i, n//i] 
                for i in range(1, int(n**0.5)+1) if n % i == 0) for x in tup)

def get_whole_div(div_size, FACTORS):
    """
    Returns closest whole number minute time_divisions to the specified division length.
    """
    distances = [abs(factor-div_size) for factor in FACTORS]
    closest = FACTORS[distances.index(min(distances))]
    return closest

# def time_to_string(time, start_minutes = 0, start_hours = 0):
#     minutes = (time + start_minutes) % 60    
#     hours = (time // 60 + start_hours) // 24 + (time // 60 + start_hours) % 24
#     return f"{hours:02}:{minutes:02}"

def time_to_string(time, start_time = 0):
    time = time + start_time
    minutes = (time) % 60    
    hours = (time // 60)
    return f"{hours:02}:{minutes:02}"


def create_time_index(div_size, total_time, start_time = None):
    """
    Formats time into HH:MM format and returns index for a dataframe
    
    Inputs
    ------
    div_size: time length of division in minutes

    Returns
    -------
    Index of times in HH:MM format
    """
    if start_time is None:
        start_time = 0
    if (start_time + total_time) > 1440:
        print("Index cannot span multiple days")
        raise IndexSpanError
    start_minutes = start_time % 60
    start_hours = start_time // 60
    time_index = []
    for t in range(total_time//div_size):
        # minutes = (t*div_size) % 60 + start_minutes    
        # hours = (t*div_size) // 60 + start_hours
        # time_index.append(f"{hours:02}:{minutes:02}")
        string_time = time_to_string((t*div_size),start_time= start_time)
        time_index.append(string_time)
    return time_index

def construct_dataframe(data, div_size, date, total_time, start_time = 0):
    """
    Create dataframe given data
    
    Inputs
    ------
    data: data from microcontroller
    div_size: time length of division
    date: The data of the data

    Returns
    -------
    Pandas dataframe of the data
    """
    time_index = create_time_index(div_size, total_time, start_time= start_time)
    if type(data) == type(None):
        data = np.full(total_time//div_size, 0)
    return pd.DataFrame(data, index=time_index, columns = pd.to_datetime([date]))
    schedule = {}
    for e,i in enumerate(data):
        schedule[time_index[e]] = i
    return pd.DataFrame(data=schedule)

def random_data(div_size):
    """
    Create randome data
    Input
    -----
    div_size: Time length of divisions

    Returns
    -------
    Randomized data
    """
    data = np.random.randint(0,2,(1440//div_size))
    return data

def add_duration(timesheet):
    """
    Calculates the duration the light has been on for. This is an extra feature that is intended to be used for machine learning purposes

    Input
    ------
    schedule: The daily timesheet dataframe 

    Returns
    -------
    Timesheet with duration column added and last duration column value
    """
    timesheet_copy = timesheet.copy()
    schedule_length = (len(timesheet_copy.index)-1)
    if "duration" in timesheet.columns:
        pass
    else:
        timesheet_copy["duration"] = ""
        for i, time in enumerate(timesheet_copy.index):
            if timesheet_copy.iloc[i][1] == 1:
                if i == 0:#first row
                    try:
                        timesheet_copy['duration'][i] = timesheet_copy['last duration'][0]
                    except KeyError:
                        timesheet_copy['duration'][i] = 0
                else:
                    timesheet_copy['duration'][i] = timesheet_copy.iloc[i][1] + timesheet_copy['duration'][(i-1)]
            else:
                timesheet_copy['duration'][i] = 0    
            if i == schedule_length:
                timesheet_copy['last duration'] = ''
                timesheet_copy['last duration'][0] = timesheet_copy['duration'][i]
    return timesheet_copy

def add_day_of_week(timesheet):
    date = timesheet.columns[1]
    year, month, day = (int(x) for x in date.split('-'))
    day = datetime(year, month, day).weekday()  
    timesheet["DayOfWeek"] = day
    return timesheet

def string_to_time_datasheet(timesheet):
    timesheet_copy = timesheet.copy()
    timesheet_copy['Time (minutes)'] = 0
    for i, time in enumerate(timesheet.index):
        timesheet_copy['Time (minutes)'][i] = string_to_time(timesheet_copy.iloc[i][0])
    return timesheet_copy

def string_to_time(string_time):
    hours, minutes = (int(x) for x in string_time.split(':'))
    total_time = (hours*60) + minutes
    return total_time

def data_structuring(timesheets):
    concatenated = pd.DataFrame()
    for timesheet in timesheets:
        columns = timesheet.columns
        timesheet = timesheet.rename(columns = {columns[1]:'State'})
        concatenated = pd.concat([concatenated, timesheet], axis=0, ignore_index=True)

    return concatenated    