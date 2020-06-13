import schedule
import time

def job(message):
    print("I'm working on...", message)

def two():
    print("Its 2:30")

schedule.every().day.at("14:37").do(two)
schedule.every().minute.at(":17").do(job, message="Testing")


while True:
    schedule.run_pending()
    time.sleep(1)    