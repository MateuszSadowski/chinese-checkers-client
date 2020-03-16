import string
import random

def removeValuesFromList(the_list, val):
   return [value for value in the_list if value != val]

def randomString(stringLength=10):
    # Generate a random string of fixed length
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))