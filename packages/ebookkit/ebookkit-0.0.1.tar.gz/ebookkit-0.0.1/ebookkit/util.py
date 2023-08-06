import os

def makedirs(d):
    try:
        os.makedirs(d)
    except OSError, e:
        if e.errno != 17:
            raise e
