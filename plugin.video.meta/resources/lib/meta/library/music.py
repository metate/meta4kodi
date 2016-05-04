import os
import shutil
import requests

from xbmcswift2 import xbmc, xbmcvfs

from meta import plugin
from meta.utils.text import to_utf8
from lastfm import lastfm


def add_music_to_library(library_folder, artist_name, album_name, track_name):
    changed = False
    artist_info = lastfm.get_artist_info(artist_name)
    album_info = lastfm.get_album_info(artist_name, album_name)

    # create nfo file
    artist_folder = os.path.join(library_folder, artist_name)
    album_folder = os.path.join(artist_folder, album_name)
    if not xbmcvfs.exists(artist_folder):
        xbmcvfs.mkdir(artist_folder)
    if not xbmcvfs.exists(album_folder):
        xbmcvfs.mkdir(album_folder)
    nfo_artist_path = os.path.join(artist_folder, "artist.nfo")
    nfo_album_path = os.path.join(album_folder, "album.nfo")
    nfo_track_path = os.path.join(album_folder, track_name + ".nfo")
    if not xbmcvfs.exists(nfo_artist_path):
        changed = True
        image = artist_info["image"][-1]["#text"]
        nfo_file = xbmcvfs.File(nfo_artist_path, 'w')
        content = "<artist>\n" \
                  "  <name>{0}</name>\n" \
                  "  <thumb>{1}</thumb>\n" \
                  "</artist>".format(artist_name, image)
        nfo_file.write(content)
        nfo_file.close()

    if not xbmcvfs.exists(nfo_album_path):
        changed = True
        image = album_info["image"][-1]["#text"]
        nfo_file = xbmcvfs.File(nfo_album_path, 'w')
        content = "<album>\n" \
                  "  <title>{0}</title>\n" \
                  "  <artist>{1}</artist>\n" \
                  "  <thumb>{2}</thumb>\n" \
                  "</album>".format(album_name, artist_name, image)
        nfo_file.write(content)
        nfo_file.close()

    if not xbmcvfs.exists(nfo_track_path):
        changed = True
        track_info = lastfm.get_track_info(artist_name, track_name)
        track_number = ""
        if "album" in track_info:
            track_number = track_info["album"]["@attr"]["position"]
        nfo_file = xbmcvfs.File(nfo_track_path, 'w')
        content = "<musicvideo>\n" \
                  "  <title>{0}</title>\n" \
                  "  <artist>{1}</artist>\n" \
                  "  <album>{2}</album>\n" \
                  "  <track>{3}</track>\n" \
                  "</musicvideo>".format(to_utf8(track_name), artist_name, album_name, track_number)
        nfo_file.write(content)
        nfo_file.close()

    # create strm file
    strm_filepath = os.path.join(album_folder, track_name + ".strm")
    if not xbmcvfs.exists(strm_filepath):
        changed = True
        track_info = lastfm.get_track_info(artist_name, track_name)
        track_number = ""
        if "album" in track_info:
            track_number = track_info["album"]["@attr"]["position"]
            strm_filepath = "{0}. {1}".format(track_number, strm_filepath)
        strm_file = xbmcvfs.File(strm_filepath, 'w')
        content = plugin.url_for("music_play", artist_name=artist_name, track_name=track_name,
                                 album_name=album_name, mode='library')
        strm_file.write(content)
        strm_file.close()

    # create thumbnails
    thumb_album_path = os.path.join(artist_folder, "folder.jpg")
    if not xbmcvfs.exists(thumb_album_path):
            changed = True
            r = requests.get(artist_info["image"][-1]["#text"], stream=True)
            if r.status_code == 200:
                try:
                    with open(thumb_album_path, 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
                except:
                    pass

    thumb_album_path = os.path.join(album_folder, "folder.jpg")
    if not xbmcvfs.exists(thumb_album_path):
            changed = True
            try:
                r = requests.get(album_info["image"][-1]["#text"], stream=True)
                if r.status_code == 200:
                    with open(thumb_album_path, 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
            except:
                pass

    return changed


def setup_library(library_folder):
    if library_folder[-1] != "/":
        library_folder += "/"

    if not xbmcvfs.exists(library_folder):
        # create folder
        xbmcvfs.mkdir(library_folder)

    # return translated path
    return xbmc.translatePath(library_folder)
