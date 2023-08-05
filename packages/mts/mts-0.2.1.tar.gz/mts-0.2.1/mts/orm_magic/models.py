import re
import requests
from django.db import models


class Show(models.Model):
    mts_id = models.PositiveIntegerField(unique=True, null=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    short_code = models.CharField(max_length=100, null=True)    # E.g: The Big Bang Theory == tbbt

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<Show %s>' % self

    @property
    def poster(self):
        return "http://sc.miratuserie.com/posters/%s.jpg" % self.slug

    @property
    def url(self):
        return "http://www.miratuserie.tv/mira-%s" % self.slug


class Episode(models.Model):
    show = models.ForeignKey(Show)
    slug = models.SlugField(max_length=200)

    mts_id = models.PositiveIntegerField(unique=True, null=True)
    season = models.IntegerField()
    episode = models.IntegerField()

    title = models.CharField(max_length=200, default="")
    overview = models.TextField(blank=True, null=True)

    @property
    def url(self):
        return 'http://www.miratuserie.tv/mira-%s/temporada-%02d/episodio-%02d/%s' % (self.show.slug,
                                                                                      self.season,
                                                                                      self.episode,
                                                                                      self.slug)
    @property
    def iframe(self):
        return "http://www.miratuserie.tv/servidores?id=%d&tc=%d%02d" % (self.mts_id, self.season, self.episode)


    @property
    def subtitle(self):
        return 'http://sc.miratuserie.com/%s/subs/%d%02d.srt' % (self.show.short_code, self.season, self.episode)

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<%s %s "%s">' % (self.show, self.number, self)

    @property
    def number(self):
        return "%02dx%02d" % (self.season, self.episode)

    @property
    def video(self):
        try:
            source = self.source_set.filter(host='pinit')[0]
        except IndexError:
            return
        response = requests.get('http://www.pinit.tv/player/vConfig_embed_new.php?vkey=%s' % source.key)
        return re.findall(r'.*\<location\>(.*)\</location\>.*', response.content, re.MULTILINE)[0]


class Source(models.Model):
    episode = models.ForeignKey(Episode)
    host = models.SlugField()
    key = models.SlugField()
    gk = models.BooleanField()
    hd = models.BooleanField()
    subs = models.BooleanField()
    plugin = models.BooleanField()
    idiomas = models.CharField(max_length=20)
