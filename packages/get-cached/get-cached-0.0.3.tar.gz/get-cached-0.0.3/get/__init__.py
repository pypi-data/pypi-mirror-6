import os

from .download import _get
from .helpers import _randomsleep, _paths

def get(url, cachedir = '.', load = True, downloader = _get, sleep = _randomsleep):
    'Download a web file, or load the version from disk.'
    local_dir, local_file = _paths(cachedir, url)

    # mkdir -p
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    # Download
    if not os.path.exists(local_file):
       with open(local_file, 'wb') as fp:
           fp.write(downloader(url))
       sleep()

    if load:
        return open(local_file).read()
