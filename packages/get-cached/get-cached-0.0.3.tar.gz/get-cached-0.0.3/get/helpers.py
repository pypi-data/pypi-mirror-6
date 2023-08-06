import os
import re
from time import sleep
from random import normalvariate

def _randomsleep(mean = 1, sd = 0.5):
    "Sleep for a random amount of time"
    seconds=normalvariate(mean, sd)
    if seconds>0:
        sleep(seconds)

def _paths(cachedir, url):
    '''
    cachedir, url -> local_dir, local_file
    '''
    tmp1 = re.sub(r'^https?://', '', url)
    tmp2 = [cachedir] + list(filter(None, tmp1.split('/')))
    local_file = os.path.join(*tmp2)
    local_dir = os.path.join(*tmp2[:-1])
    return local_dir, local_file
