__author__ = 'Andrew <andrew@codeusa523.org>'
__version__ = '3.0'
import urllib2
import json


api_url = 'http://netflixroulette.net/api/api.php?'
version = '3.0'


def get_version():
    return version


def get_media_rating(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "%stitle=%s&year=%d" % (api_url, title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload[0]['rating']
    else:
        return 'Unable to locate data'


def get_media_poster(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "%stitle=%s&year=%d" % (api_url, title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload[0]['poster']
    else:
        return 'Unable to locate data'


def get_media_type(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "%stitle=%s&year=%d" % (api_url, title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload[0]['mediatype']
    else:
        return 'Unable to locate data'


def get_media_release_year(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "%stitle=%s&year=%d" % (api_url, title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload[0]['release_year']
    else:
        return 'Unable to locate data'


def get_media_cast(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "%stitle=%s&year=%d" % (api_url, title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload[0]['show_cast']
    else:
        return 'Unable to locate data'


def get_media_category(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "%stitle=%s&year=%d" % (api_url, title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload[0]['category']
    else:
        return 'Unable to locate data'


def get_media_summary(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "http://codeusa.net/apps/netflix/api/api.php?title=%s&year=%d" % (title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload[0]['summary']
    else:
        return 'Unable to locate data'


def get_media_director(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "%stitle=%s&year=%d" % (api_url, title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload[0]['director']
    else:
        return 'Unable to locate data'


def get_netflix_id(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "%stitle=%s&year=%d" % (api_url, title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload[0]['show_id']
    else:
        return 'Unable to locate data'


def get_all_data(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    url = "%stitle=%s&year=%d" % (api_url, title, year)
    request = urllib2.Request(url)
    payload = json.load(urllib2.urlopen(request))
    if 'error' not in payload:
        return payload
    else:
        return 'Unable to locate data'


# No more please
