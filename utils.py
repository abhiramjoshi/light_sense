import numpy as np
import pandas as pd

def factors(n):
    return set(x for tup in ([i, n//i] 
                for i in range(1, int(n**0.5)+1) if n % i == 0) for x in tup)

def get_whole_div(div_size, FACTORS):
    distances = [abs(factor-div_size) for factor in FACTORS]
    closest = FACTORS[distances.index(min(distances))]
    return closest

def create_time_index(div_size):
    time_index = []
    for t in range(1440//div_size):
        minutes = (t*div_size) % 60     
        hours = (t*div_size) // 60
        time_index.append(f"{hours:02}:{minutes:02}")
    return time_index

def construct_dataframe(data, div_size, date):
    time_index = create_time_index(div_size)
    if type(data) == type(None):
        data = np.full(1440//div_size, 0)
    return pd.DataFrame(data, index=time_index, columns = pd.to_datetime([date]))
    schedule = {}
    for e,i in enumerate(data):
        schedule[time_index[e]] = i
    return pd.DataFrame(data=schedule)

def random_data(div_size):
    data = np.random.randint(0,2,(1440//div_size))
    return data
