import requests
from meta.utils.text import to_utf8
from meta import plugin, LANG
from settings import *

API_KEY = "1"
API_ENDPOINT = "http://www.theaudiodb.com/api/v1/json/{0}".format(API_KEY)


def call_audiodb(path, params={}):
    params = dict([(k, to_utf8(v)) for k, v in params.items() if v])
    response = requests.get("{0}/{1}.php".format(API_ENDPOINT, path), params)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response.json()


@plugin.cached(TTL=CACHE_TTL, cache="audiodb")
def search_artist(artist_name):
    return call_audiodb("search", params={'Artist': name})


@plugin.cached(TTL=CACHE_TTL, cache="audiodb")
def search_artist_albums(artist_name):
    return call_audiodb("searchalbum", params={'Artist': name})


@plugin.cached(TTL=CACHE_TTL, cache="audiodb")
def search_artist_album(artist_name, album_name):
    return call_audiodb("searchalbum", params={'Artist': name, 'a': album_name})


