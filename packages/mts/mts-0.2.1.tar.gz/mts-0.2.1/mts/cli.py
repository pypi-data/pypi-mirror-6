"""
mts -- miratuserie.tv in your command line

Usage:
    mts [-i] [-ns] [-d] <show> <start>
    mts -i


Arguments:
  title                 Looks for a show. Like 'how i met' or 'big bang'

  start                 Specifies a season/episode of a show to start play.
                        Examples: S01 (a whole season), s02e04 or 9x13

optional arguments:
  -i, --info            Show info about available shows and episodes
  -h, --help            Show this help message and exit
  -n, --no-subtitles    Don't download subtitles
  -d, --download        Download the episode instead play it (TO DO)
"""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mts.settings")


import re
import subprocess
import tempfile
from ConfigParser import SafeConfigParser

APP_DATA_DIR = os.path.join(os.path.expanduser("~"), '.mts')
CONFIG_FILE = os.path.join(APP_DATA_DIR, 'config.ini')

import requests
from docopt import docopt

from mts.orm_magic.models import Show


def get_numbers(s):
    """Extracts all integers from a string an return them in a list"""

    result = map(int, re.findall(r'[0-9]+', unicode(s)))
    return result + [1] * (2 - len(result))


def urlretrieve(url):
    r = requests.get(url)
    _, filename = tempfile.mkstemp(suffix='.srt')
    with open(filename, 'wb') as f:
        f.write(r.content)
    return filename


def main():
    args = docopt(__doc__)

    if args['--info'] and args['<show>'] is None:
        print("Available shows:\n")
        for s in Show.objects.all():
            print(s)
        return


    show = Show.objects.filter(title__icontains=args['<show>'])

    if show.count() == 0:
        sys.exit('Show not found')
    elif show.count() > 1:
        multi = '\n'.join(map(str, show))
        sys.exit('Show name is ambiguos: \n\n%s' % multi)

    show = show[0]
    player = get_config().get('main', 'player')
    season, episode_number = get_numbers(args['<start>'])


    for i, episode in enumerate(show.episode_set.filter(season=season,
                                           episode__gte=episode_number)):

        try:
            if args['--info'] and i == 0:
                title = repr(episode)[1:-1]
                print(title)
                print('-' * len(title))
                print('')
                print(episode.overview)
                return

            print("Retrieving %s %s..." % (show, episode.number))
            if not episode.video:
                sys.exit('No pinit source for this episode')


            arguments = player.replace('{episode}', episode.video)

            subs_pattern = re.findall('.*(\[(.*\{subs\})\]).*',
                                      arguments)

            if args['--no-subtitles'] and subs_pattern:

                arguments = arguments.replace(subs_pattern[0][0], '')
            elif subs_pattern:
                subs = urlretrieve(episode.subtitle)
                arguments = arguments.replace(*subs_pattern[0]).replace('{subs}', subs)

            subprocess.call(arguments.split())

        except KeyboardInterrupt:
            sys.exit('\nSee you!')


def get_config():

    DEFAULTS = { 'main': {
                    "player": "mplayer -fs {episode} [-sub {subs}]",
                    },
                }

    config = SafeConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print "There is no config file. Creating default in %s" % CONFIG_FILE
        for section, options in DEFAULTS.items():
            for section, options in DEFAULTS.items():
                if not config.has_section(section):
                    config.add_section(section)
                for option, value in options.items():
                    config.set(section, option, value)

        if not os.path.exists(APP_DATA_DIR):
            os.makedirs(APP_DATA_DIR)   #make .mts dir
        with open(CONFIG_FILE, 'w') as cfg:
            config.write(cfg)
    else:
        with open(CONFIG_FILE, 'r') as cfg:
            config.readfp(cfg)
    return config


if __name__ == '__main__':
    main()