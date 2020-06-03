import numpy as np
import pandas as pd

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

def create_time_index(div_size):
    """
    Formats time into HH:MM format and returns index for a dataframe
    
    Inputs
    ------
    div_size: time length of division in minutes

    Returns
    -------
    Index of times in HH:MM format
    """

    time_index = []
    for t in range(1440//div_size):
        minutes = (t*div_size) % 60     
        hours = (t*div_size) // 60
        time_index.append(f"{hours:02}:{minutes:02}")
    return time_index

def construct_dataframe(data, div_size, date):
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
    time_index = create_time_index(div_size)
    if type(data) == type(None):
        data = np.full(1440//div_size, 0)
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
