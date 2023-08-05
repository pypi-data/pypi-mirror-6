import re
import sys
import time
import requests


def _countdown(seconds):
    """
    Wait `seconds` counting down.
    """
    for i in range(seconds, 0, -1):
        sys.stdout.write("%02d" % i)
        time.sleep(1)
        sys.stdout.write("\b\b")
        sys.stdout.flush()
    sys.stdout.flush()


def pinit(episode):
    try:
        source = episode.source_set.filter(host='pinit')[0]
    except IndexError:
        return
    response = requests.get('http://www.pinit.tv/player/vConfig_embed_new.php?vkey=%s' % source.key)
    return re.findall(r'.*\<location\>(.*)\</location\>.*', response.content, re.MULTILINE)[0]


def uptobox(episode):
    try:
        source = episode.source_set.filter(host='uptobox')[0]
    except IndexError:
        return

    response = requests.post('http://uptobox.com/%s' % source.key,
                             {"op": "download1",
                              "id": source.key,
                              "method_free": "Free Download"})
    rand = re.findall("rand\" value=\"(.*)\"", response.content)
    _countdown(60)
    response = requests.post('http://uptobox.com/%s' % source.key,
                         {"op": "download2",
                          "id": source.key,
                          "rand": rand,
                          "method_free": "Free Download"})
    return re.findall("a href=\"(.*)\">Click", response.content)[0]