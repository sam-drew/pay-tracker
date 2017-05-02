from datetime import datetime

startTime = input("Enter start time: ")
finishTime = input("Enter finish time: ")
startTime = datetime.strptime(startTime, '%H:%M')
finishTime = datetime.strptime(finishTime, '%H:%M')
timedelta = finishTime - startTime
print(timedelta)
