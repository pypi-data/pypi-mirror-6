import tempfile, os
import shutil

from get import get
from get.helpers import _paths

def test_get():
    downloader = lambda _:b'abcde'
    cachedir = tempfile.mkdtemp()
    sleep = lambda:None
    url = 'http://foo.bar/baz'

    observed = get(url, cachedir = cachedir, downloader = downloader,
                   sleep = sleep, load = True)
    assert observed == downloader(None), (observed, downloader(None))

    shutil.rmtree(cachedir)

def test_read_cache():
    downloader = lambda _:b'abcde'
    cachedir = tempfile.mkdtemp()
    sleep = lambda:None
    url = 'http://foo.bar/baz'
    os.makedirs(os.path.join(cachedir, 'foo.bar'))

    expected = b'lalalala'

    with open(os.path.join(cachedir, 'foo.bar', 'baz'), 'wb') as fp:
        fp.write(expected)

    observed = get(url, cachedir = cachedir, downloader = downloader,
                   sleep = sleep, load = True)
    assert observed == expected, (observed, expected)
    shutil.rmtree(cachedir)

def test_load_off():
    downloader = lambda _:b'abcde'
    cachedir = tempfile.mkdtemp()
    sleep = lambda:None
    url = 'http://foo.bar/baz'
    os.makedirs(os.path.join(cachedir, 'foo.bar'))

    observed = get(url, cachedir = cachedir, downloader = downloader,
                   sleep = sleep, load = False)
    assert observed == None

    shutil.rmtree(cachedir)

def test_write_cache():
    downloader = lambda _:b'abcde'
    cachedir = tempfile.mkdtemp()
    sleep = lambda:None
    url = 'http://foo.bar/baz'
    os.makedirs(os.path.join(cachedir, 'foo.bar'))

    get(url, cachedir = cachedir, downloader = downloader,
        sleep = sleep, load = False)

    with open(os.path.join(cachedir, 'foo.bar', 'baz'), 'rb') as fp:
        read = fp.read()
    assert read == downloader(None)

    shutil.rmtree(cachedir)

def test_paths():
    observed = _paths('abc','http://la.la/la')
    expected = os.path.join('abc','la.la'), os.path.join('abc','la.la','la')
    assert observed == expected, (observed, expected)
