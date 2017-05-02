from datetime import datetime

startTime = input("Enter start time: ")
finishTime = input("Enter finish time: ")
startTime = datetime.strptime(startTime, '%H:%M')
finishTime = datetime.strptime(finishTime, '%H:%M')
timeDelta = finishTime - startTime
timeDeltaSeconds = timeDelta.seconds
timeDeltaDecimalHours = timeDeltaSeconds / 3600
if timeDeltaDecimalHours <= 3.75:
    breakLength = 0
elif timeDeltaDecimalHours <= 5.75:
    breakLength = 0.25
elif timeDeltaDecimalHours <= 7.75:
    breakLength = 0.5
elif timeDeltaDecimalHours <= 8.75:
    breakLength = 0.75
else:
    breakLength = 1.5
print("Break length is calculated to be:", breakLength)
breakCorrect = input("Is the break length correct? (y/n)")
while breakCorrect != "y" and breakCorrect != "n":
    breakCorrect = "Please enter y or n: "
if breakCorrect == "n":
    breakLength = input("Please enter the correct length of your break: ")
