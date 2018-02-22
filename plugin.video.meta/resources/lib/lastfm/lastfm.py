# -*- coding: utf-8 -*-
import requests
from meta.utils.text import to_utf8
from meta import plugin, LANG
from settings import *

API_ENDPOINT = "http://ws.audioscrobbler.com/2.0/"
API_KEY = "190ca7b33906fd52342ee2d9c4d88ea8"
SHARED_SECRET = "2c633c8d408032e1883789af6ad3a49d"


def call_last_fm(params={}, data=None, result_format="json"):
    params = dict([(k, to_utf8(v)) for k, v in params.items() if v])
    params["api_key"] = API_KEY
    params["format"] = result_format

    def send_query():
        if data is not None:
            assert not params
            return requests.post("{0}".format(API_ENDPOINT), json=data)
        else:
            return requests.get("{0}".format(API_ENDPOINT), params)

    response = send_query()
    response.raise_for_status()
    response.encoding = 'utf-8'
    if result_format == "json":
        return response.json()
    else:
        return response.text


@plugin.cached(TTL=CACHE_TTL, cache="lastfm")
def search_artist(artist_name, page=1):
    parameters = {}
    parameters['method'] = 'artist.search'
    parameters['artist'] = artist_name
    parameters["limit"] = 25
    parameters["page"] = page

    results = call_last_fm(parameters)["results"]
    return results


@plugin.cached(TTL=CACHE_TTL, cache="lastfm")
def search_album(album_name, page=1):
    parameters = {}
    parameters['method'] = 'album.search'
    parameters['album'] = album_name
    parameters["limit"] = 25
    parameters["page"] = page

    results = call_last_fm(parameters)["results"]
    return results


@plugin.cached(TTL=CACHE_TTL, cache="lastfm")
def search_track(track_name, page=1):
    parameters = {}
    parameters['method'] = 'track.search'
    parameters['track'] = track_name
    parameters["limit"] = 25
    parameters["page"] = page

    results = call_last_fm(parameters)["results"]
    return results


@plugin.cached(TTL=CACHE_TTL, cache="lastfm")
def get_artist_top_tracks(artist_name, page):
    parameters = {}
    parameters['method'] = 'artist.gettoptracks'
    parameters["artist"] = artist_name
    parameters["page"] = page
    results = call_last_fm(parameters)
    return results["toptracks"]


@plugin.cached(TTL=CACHE_TTL, cache="lastfm")
def get_artist_top_albums(artist_name, page=1):
    parameters = {}
    parameters['method'] = 'artist.gettopalbums'
    parameters["artist"] = artist_name
    parameters["page"] = page
    results = call_last_fm(parameters)
    return results["topalbums"]


@plugin.cached(TTL=CACHE_TTL, cache="lastfm")
def get_track_info(artist_name, track_name):
    parameters = {}
    parameters['method'] = 'track.getinfo'
    parameters["artist"] = artist_name
    parameters["track"] = track_name
    results = call_last_fm(parameters)
    return results["track"]


@plugin.cached(TTL=CACHE_TTL, cache="lastfm")
def get_album_info(artist_name, album_name):
    parameters = {}
    parameters['method'] = 'album.getinfo'
    parameters["artist"] = artist_name
    parameters["album"] = album_name
    results = call_last_fm(parameters)
    return results["album"]


@plugin.cached(TTL=CACHE_TTL, cache="lastfm")
def get_artist_info(artist_name):
    parameters = {}
    parameters['method'] = 'artist.getinfo'
    parameters["artist"] = artist_name
    results = call_last_fm(parameters)
    return results["artist"]
