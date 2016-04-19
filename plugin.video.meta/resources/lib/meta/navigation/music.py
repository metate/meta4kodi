from meta import plugin, LANG
from meta.gui import dialogs
from meta.utils.text import to_utf8
from meta.play.players import ADDON_DEFAULT, ADDON_SELECTOR
from meta.play.music import play_music, play_music_video
from meta.navigation.base import search, get_icon_path, get_genre_icon, get_genres, get_tv_genres, \
    caller_name, caller_args
from meta.library.music import setup_library, add_music_to_library
from meta.library.tools import scan_library
from language import get_string as _
from settings import SETTING_MUSIC_LIBRARY_FOLDER

from lastfm import lastfm


@plugin.route('/music')
def music():
    items = [
        {
            'label': _("Search Artist"),
            'path': plugin.url_for("music_search_artist"),
            'icon': get_icon_path("search"),
        },
        {
            'label': _("Search Album"),
            'path': plugin.url_for("music_search_album"),
            'icon': get_icon_path("search"),
        },
        {
            'label': _("Search Track"),
            'path': plugin.url_for("music_search_track"),
            'icon': get_icon_path("search"),
        },
    ]
    return items


@plugin.route('/music/search/artist')
def music_search_artist():
    search(music_search_artist_term)


@plugin.route('/music/search/album')
def music_search_album():
    search(music_search_album_term)


@plugin.route('/music/search/track')
def music_search_track():
    search(music_search_track_term)


@plugin.route('/music/search_artist_term/<term>/<page>')
def music_search_artist_term(term, page):
    search_results = lastfm.search_artist(term, page)
    artists = search_results["artistmatches"]["artist"]
    items_per_page = search_results["opensearch:itemsPerPage"]
    start_index = search_results["opensearch:startIndex"]
    total_results = search_results["opensearch:totalResults"]
    items = []
    for artist in artists:
        large_image = artist["image"][2]["#text"]
        name = to_utf8(artist["name"])
        item = {
            'label': name,
            'path': plugin.url_for(music_artist, name=name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': name,
            },
            'info_type': 'music',
        }

        items.append(item)
    if start_index + items_per_page < total_results:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_search_artist_term, term=term, page=int(page) + 1)
        })
    return items


@plugin.route('/music/search_album_term/<term>/<page>')
def music_search_album_term(term, page):
    search_results = lastfm.search_album(term, page)
    albums = search_results["albummatches"]["album"]
    items_per_page = search_results["opensearch:itemsPerPage"]
    start_index = search_results["opensearch:startIndex"]
    total_results = search_results["opensearch:totalResults"]
    items = []
    for album in albums:
        large_image = album["image"][2]["#text"]
        album_name = to_utf8(album["name"])
        artist_name = to_utf8(album["artist"])
        item = {
            'label': "{0} - {1}".format(artist_name, album_name),
            'path': plugin.url_for(music_artist_album_tracks, artist_name=artist_name, album_name=album_name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': artist_name,
            },
            'info_type': 'music',
        }

        items.append(item)
    if start_index + items_per_page < total_results:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_search_album_term, term=term, page=int(page) + 1)
        })
    return items


@plugin.route('/music/search_track_term/<term>/<page>')
def music_search_track_term(term, page):
    search_results = lastfm.search_track(term, page)
    tracks = search_results["trackmatches"]["track"]
    items_per_page = search_results["opensearch:itemsPerPage"]
    start_index = search_results["opensearch:startIndex"]
    total_results = search_results["opensearch:totalResults"]
    items = []
    for track in tracks:
        large_image = track["image"][2]["#text"]
        track_name = to_utf8(track["name"])
        artist_name = to_utf8(track["artist"])
        item = {
            'label': "{0} - {1}".format(artist_name, track_name),
            'path': plugin.url_for(music_play, artist_name=artist_name, track_name=track_name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': artist_name,
            },
            'info_type': 'music',
        }

        items.append(item)
    if start_index + items_per_page < total_results:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_search_track_term, term=term, page=int(page) + 1)
        })
    return items


@plugin.route('/music/artist/<name>')
def music_artist(name):
    name = to_utf8(name)
    items = [
        {
            'label': _("Tracks"),
            'path': plugin.url_for("music_artist_tracks", artist_name=name),
            'icon': get_icon_path("music")
        },
        {
            'label': _("Albums"),
            'path': plugin.url_for("music_artist_albums", artist_name=name),
            'icon': get_icon_path("music")
        },
    ]
    return items


@plugin.route('/music/artist/<artist_name>/tracks/<page>', options={'page': "1"})
def music_artist_tracks(artist_name, page):
    artist_name = to_utf8(artist_name)
    results = lastfm.get_artist_top_tracks(artist_name, page)
    items = []
    for track in results["track"]:
        large_image = track["image"][2]["#text"]
        track_name = to_utf8(track["name"])
        context_menu = [
            (
                _("Select stream..."),
                "PlayMedia({0})".format(plugin.url_for("music_play", artist_name=artist_name,
                                                       track_name=track_name, mode='select'))
            ),
            # not working
            # (
            #     _("Add to library"),
            #     "RunPlugin({0})".format(plugin.url_for("music_add_to_library", artist_name = artist_name,
            #                                            track_name = track["name"]))
            # )
        ]
        item = {
            'label': track_name,
            'path': plugin.url_for("music_play", artist_name=artist_name, track_name=track_name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info_type': 'music',
            'context_menu': context_menu,
        }
        items.append(item)
    if results["@attr"]["totalPages"] > page:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_artist_tracks, artist_name=artist_name, page=int(page) + 1)
        })
    return items


@plugin.route('/music/artist/<artist_name>/albums/<page>', options={'page': "1"})
def music_artist_albums(artist_name, page):
    artist_name = to_utf8(artist_name)
    results = lastfm.get_artist_top_albums(artist_name, page)
    items = []
    for album in results["album"]:
        album_name = to_utf8(album["name"])
        image = album['image'][-1]['#text']
        artist_album_name = to_utf8(album['artist']['name'])
        item = {
            'thumbnail': image,
            'label': "{0} - {1}".format(artist_album_name, album_name),
            'info': {
                'title': album_name,
                'artist': [artist_album_name],
            },
            'info_type': 'music',
            'path': plugin.url_for("music_artist_album_tracks", artist_name=artist_name, album_name=album_name),
        }
        items.append(item)
    if results["@attr"]["totalPages"] > page:
        next_page = int(page) + 1
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for(music_artist_albums, artist_name=artist_name, page=next_page)
        })
    return items


@plugin.route('/music/artist/<artist_name>/album/<album_name>/tracks')
def music_artist_album_tracks(artist_name, album_name):
    artist_name = to_utf8(artist_name)
    album_name = to_utf8(album_name)
    results = lastfm.get_album_info(artist_name, album_name)
    items = []
    for track in results["tracks"]["track"]:
        track_name = to_utf8(track["name"])
        track_number = track["@attr"]["rank"]
        image = results["image"][-1]["#text"]
        context_menu = [
            (
                _("Select stream..."),
                "PlayMedia({0})".format(plugin.url_for("music_play", artist_name=artist_name,
                                                       track_name=track_name, mode='select'))
            ),
        ]
        item = {
            'label': "{0}. {1}".format(track_number, track_name),
            'path': plugin.url_for("music_play", artist_name=artist_name, album_name=album_name,
                                   track_name=track_name),
            'thumbnail': image,
            'icon': "DefaultMusic.png",
            'poster': image,
            'info_type': 'music',
            'context_menu': context_menu,
        }
        items.append(item)
    return items


@plugin.route('/music/play/<artist_name>/<track_name>/<album_name>/<mode>', options={'album_name': "None",
                                                                                     'mode': 'default'})
def music_play(artist_name, track_name, album_name, mode):
    items = [
        {
            'label': _("Play Audio"),
            'path': plugin.url_for("music_play_audio", artist_name=artist_name, track_name=track_name,
                                   album_name=album_name, mode=mode)
        },
        {
            'label': _("Play Video"),
            'path': plugin.url_for("music_play_video", artist_name=artist_name, track_name=track_name,
                                   album_name=album_name, mode=mode)
        }
    ]
    return items


@plugin.route('/music/play_audio/<artist_name>/<track_name>/<album_name>/<mode>', options={'album_name': "None",
                                                                                           'mode': 'default'})
def music_play_audio(artist_name, track_name, album_name, mode):
    if album_name == "None":
        track_info = lastfm.get_track_info(artist_name, track_name)
        if track_info and "album" in track_info:
            album_name = track_info["album"]["title"]
    play_music(artist_name, track_name, album_name, mode)


@plugin.route('/music/play_video/<artist_name>/<track_name>/<album_name>/<mode>', options={'album_name': "None",
                                                                                           'mode': 'default'})
def music_play_video(artist_name, track_name, album_name, mode):
    if album_name == "None":
        track_info = lastfm.get_track_info(artist_name, track_name)
        if track_info and "album" in track_info:
            album_name = track_info["album"]["title"]
    play_music_video(artist_name, track_name, album_name, mode)


@plugin.route('/music/add_to_library/<artist_name>/<track_name>/<album_name>', options={'album_name': "None"})
def music_add_to_library(artist_name, track_name, album_name):
    if album_name == "None":
        album_name = lastfm.get_track_info(artist_name, track_name)["album"]["title"]

    library_folder = setup_library(plugin.get_setting(SETTING_MUSIC_LIBRARY_FOLDER))

    add_music_to_library(library_folder, artist_name, album_name, track_name)
    scan_library()
