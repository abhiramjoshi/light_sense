import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import pandas as pd
import light_sense as ls
import utils as u
from datetime import datetime, timedelta

TOTAL_TIME = 1440
##load data

##add features

class NoModel(Exception):
    pass

def batch_complete_data(complete_data):
    if len(complete_data.columns)%7 == 0:
        complete_data_batch = complete_data.iloc[-7:]
        return complete_data_batch
    else:
        print("Not enough data to form new training batch")
        return None

def add_prev_state(timesheet, prev_last_duration=0):
    timesheet['prev state'] = ""
    for i, time in enumerate(timesheet.index):
        if i == 0:
            timesheet['prev state'][i] = prev_last_duration
        else:
            timesheet['prev state'][i] = timesheet.iloc[i-1][0]
    return timesheet

def add_features_test(timesheets_provided):
    timesheets = []
    prev_last_duration = 0
    for timesheet in timesheets_provided:
        #timesheet, prev_last_duration = u.add_duration(timesheet, prev_last_duration=prev_last_duration)
        timesheet = add_prev_state(timesheet, prev_last_duration=prev_last_duration)
        timesheet = u.add_day_of_week_test(timesheet)
        timesheet = u.string_to_time_datasheet(timesheet)
        timesheets.append(timesheet)

    structured_data = u.data_structuring(timesheets)
    return structured_data

def add_features(complete_data):
    timesheets = []
    prev_last_duration = None
    for column in complete_data.columns:
        date = column.strftime("%Y-%m-%d")
        try:
            timesheet = pd.read_csv(f'/home/aj/Documents/light_sense/data/{date}_data.csv', index_col=0)
            #timesheet, prev_last_duration = u.add_duration(timesheet, prev_last_duration=prev_last_duration)
            timesheet = u.string_to_time_datasheet(timesheet)
            timesheet["Time (minutes)"] = timesheet["Time (minutes)"]/TOTAL_TIME
            timesheet = u.day_of_week_one_hot(timesheet)
            #timesheet = u.add_day_of_week(timesheet)
            timesheets.append(timesheet)
        except FileNotFoundError:
            print(f"No data collected for {date}")

    structured_data = u.data_structuring(timesheets)
    structured_data = pd.get_dummies(structured_data, prefix="", prefix_sep="")
    return structured_data

def prepare_data_tensor(data):
    labels = data.pop("State").astype(float)
    features = data.astype(float)
    # print(labels.values)
    # print(features.values)
    data_tensor = tf.data.Dataset.from_tensor_slices((features.values, labels.values))
    #data_tensor = data_tensor.shuffle(720)
    for feat, targ in data_tensor.take(5):
        print ('Features: {}, Label: {}'.format(feat, targ))
    return data_tensor.batch(1)

def create_and_compile_model(input_shape):
    model = keras.Sequential([
        layers.Dense(64, activation='relu', input_shape=[input_shape]),
        layers.Dense(1)
    ])

    model.compile(
        optimizer='adam',
        loss = keras.losses.BinaryCrossentropy(from_logits=True),
        metrics = ["accuracy"]
    )

    return model

def save_model(model):
    model.save(filepath="./scheduler_model")

def load_model():
    try:
        model = tf.keras.models.load_model('./scheduler_model')
        return model
    except OSError:
        print("No model exists, creating new model")
        raise NoModel

def train_model(complete_data):
    training_data = batch_complete_data(complete_data)
    if training_data is None:
        print("Model was not updated/created")
        return None, model
    else:
        training_data = add_features(training_data)
        training_data_tensor = prepare_data_tensor(training_data)
        try:
            model = load_model()
        except NoModel:
            model = create_and_compile_model(len(training_data.columns))
        history = model.fit(training_data_tensor, epochs=5)
        save_model(model)
        return history, model

def predict_time_instance(time, date, model):
    """
    Predict the state of the light at a given time, based on previous collected data

    Input:
    
        time: time the prediction needs to be made. Given in string format "HH:MM"
        date: date of the prediction. Given in format "%yyyy-%mm-%dd"
        model: the trained model
        
    Returns:

        prediction: prediction of the state of the light (1 or 0).
    """
    year, month, day = (int(x) for x in date.split('-'))
    day = datetime(year, month, day).strftime("%A")
    time = u.string_to_time(time)/TOTAL_TIME
    predict_vector = pd.DataFrame(np.array([time]), columns=[date])
    predict_vector = u.day_of_week_one_hot(predict_vector)
    prediction = model.predict(predict_vector.values)
    prediction_class = tf.nn.sigmoid(prediction).numpy()[0,0]
    return int(round(prediction_class))

def predict_schedule(date):
    try:
        model = load_model()
    except NoModel:
        print("Schedule has not been create, not enough batch data")
        return None
    time_index = u.create_time_index(ls.DIV_SIZE, ls.TOTAL_TIME)
    schedule = pd.DataFrame(index=time_index, columns = [date])
    for time in time_index:
        schedule.loc[time] = predict_time_instance(time, date, model)
    return schedule

if __name__ == "__main__":
    data_1 = pd.read_csv('/home/aj/Documents/light_sense/data/2020-06-25_data.csv', index_col=0)
    data_2 = pd.read_csv('/home/aj/Documents/light_sense/data/2020-06-26_data.csv', index_col=0)
    data_3 = pd.read_csv('/home/aj/Documents/light_sense/data/2020-06-27_data.csv', index_col=0)
    data_4 = pd.read_csv('/home/aj/Documents/light_sense/data/2020-06-28_data.csv', index_col=0)
    data_5 = pd.read_csv('/home/aj/Documents/light_sense/data/2020-06-29_data.csv', index_col=0)
    data_6 = pd.read_csv('/home/aj/Documents/light_sense/data/2020-06-30_data.csv', index_col=0)
    data_7 = pd.read_csv('/home/aj/Documents/light_sense/data/2020-07-01_data.csv', index_col=0)
    data_1 = ls.TimeSheet(timesheet=data_1)
    data_2 = ls.TimeSheet(timesheet=data_2)
    data_3 = ls.TimeSheet(timesheet=data_3)
    data_4 = ls.TimeSheet(timesheet=data_4)
    data_5 = ls.TimeSheet(timesheet=data_5)
    data_6 = ls.TimeSheet(timesheet=data_6)
    data_7 = ls.TimeSheet(timesheet=data_7)
    # data_1 = ls.TimeSheet(data='ones', date=datetime.now() + timedelta(days=1))
    # data_2 = ls.TimeSheet(data='random', date=datetime.now() + timedelta(days=2))
    # data_3 = ls.TimeSheet(data='ones')
    complete_data = ls.compile_data([data_1, data_2, data_3, data_4, data_5, data_6, data_7])
    _, model = train_model(complete_data)
    predicted_schedule = predict_schedule("2020-07-02")
    print(predicted_schedule)
    predicted_schedule.to_csv('./data/predicted_schedule.csv')
    # structured_data = add_features(complete_data)
    # print(structured_data)
    # training_data = prepare_data_tensor(structured_data)
    # model = create_and_compile_model(6)
    # history = model.fit(training_data, epochs=5)
    # print(history.history)
    #test = np.array([[1, 0, 0, 0, 0, 0],[0,0,0,0,0,1], [0.923,0,0,0,0,0],])
    
    #prediction = model.predict(test)
    #print(tf.nn.sigmoid(prediction))

#prepare as tensor
#create model
#create schedule