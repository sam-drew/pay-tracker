from datetime import datetime

hourlyPay = float(input("Please enter your hourly rate of pay (as a decimal in £): "))
startTime = input("Enter start time: ")
finishTime = input("Enter finish time: ")
startTime = datetime.strptime(startTime, '%H:%M')
finishTime = datetime.strptime(finishTime, '%H:%M')
timeDelta = finishTime - startTime
timeDeltaSeconds = timeDelta.seconds
timeDeltaDecimalHours = timeDeltaSeconds / 3600
breakLength = float(input("Please enter the correct length of your break: "))
paidHours = timeDeltaDecimalHours - breakLength
print("You will be paid for", paidHours, "hours.")
print("For a total of £" + str(paidHours * hourlyPay))
