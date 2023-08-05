'''Generate Random passwords with by-default Min 
2 numeric, 2 alpha, 2 special symbols and length 8
'''

import random
import string

def getPassword(passwrd_len = 8, 
            alpha_len = 2, 
            numeric_len = 2,
            special_len = 2):
    '''    
    http://code.activestate.com/recipes/578467/
    '''
    alpha   = string.ascii_letters
    numeric = string.digits
    special = string.punctuation
    password = [random.choice(alpha) for x in range(alpha_len)]
    password += [random.choice(numeric) for x in range(numeric_len)]
    password += [random.choice(special) for x in range(special_len)]
    length = passwrd_len - (alpha_len + numeric_len + special_len)
    password += [random.choice(special + numeric + special) for x in range(length)]
    random.shuffle(password)
    return ''.join(password)
