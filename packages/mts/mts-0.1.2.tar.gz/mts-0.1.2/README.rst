
===========================================
mts, miratuserie.tv on the command line
===========================================

`miratuserie.tv <http://miratuserie.tv>`_ is a site to stream tv shows with spanish subtitles. ``mts`` do the same, but in a geek (yonkie) way.


.. attention::

    At this moment, only episodes having a source in Pinit.tv could be played.


Install
----------

::

    $ pip install mts

Usage
------

This will show the whole 3º season of *How I met your mother*::

    $ mts 'how i met' s03e01

The complete inline help looks like this::

    (mts)tin@morochita:~$ mts -h
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
      -ns, --no_subtitle    Don't download subtitles (TO DO)
      -d, --download        Download the episode instead play it (TO DO)


Configuration
--------------

Not so much by the moment, but you can set your prefered player
in ``~/.mts/config.ini``.

By default, ``mts`` tries to use ``mplayer`` in full-screen,
with this config file::

    [main]
    player = mplayer -fs {episode} -sub {subs}


For example, if you want to use ``vlc``, something like this should work::

    [main]
    player = vlc -f {episode} :sub-file={subs}

you got the idea.




* Free software: BSD license
