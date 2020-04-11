import string
import random
import os
import errno

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

def maxes(a, key=None):
    if key is None:
        key = lambda x: x
    m, max_list = key(a[0]), []
    for s in a:
        k = key(s)
        if k > m:
            m, max_list = k, [s]
        elif k == m:
            max_list.append(s)
    return m, max_list

def createDirs(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise