import string
import random

def removeValuesFromList(theList, val):
   return [value for value in theList if value != val]

def randomString(stringLength=10):
    # Generate a random string of fixed length
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def getIntegersFromConsole():
   value = -1
   while value == -1:
    try:
        value = int(input())
    except:
        print('Invalid game ID. Please input only integers')
   return value

def mergeDicts(dict1, dict2):
    merged = dict1.copy()   # start with x's keys and values
    merged.update(dict2)    # modifies z with y's keys and values & returns None
    return merged