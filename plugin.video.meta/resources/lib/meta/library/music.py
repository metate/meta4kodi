import os

from xbmcswift2 import xbmc, xbmcvfs

from meta import plugin

def add_music_to_library(library_folder, artist_name, album_name, track_name):
    changed = False

    # create nfo file
    artist_folder = os.path.join(library_folder, artist_name)
    album_folder = os.path.join(artist_folder, album_name)
    if not xbmcvfs.exists(artist_folder):
        xbmcvfs.mkdir(artist_folder)
    if not xbmcvfs.exists(album_folder):
        xbmcvfs.mkdir(album_folder)
    nfo_artist_path = os.path.join(artist_folder, "artist.nfo")
    nfo_album_path = os.path.join(album_folder, "album.nfo")
    if not xbmcvfs.exists(nfo_artist_path):
        changed = True
        nfo_file = xbmcvfs.File(nfo_artist_path, 'w')
        content = "<artist><name>{0}</name></artist>".format(artist_name)
        nfo_file.write(content)
        nfo_file.close()

    if not xbmcvfs.exists(nfo_album_path):
        changed = True
        nfo_file = xbmcvfs.File(nfo_album_path, 'w')
        content = "<album><title>{0}</title><artist>{1}</artist></album>".format(album_name, artist_name)
        nfo_file.write(content)
        nfo_file.close()

    # create strm file
    strm_filepath = os.path.join(album_folder, track_name + ".strm")
    if not xbmcvfs.exists(strm_filepath):
        changed = True
        strm_file = xbmcvfs.File(strm_filepath, 'w')
        content = plugin.url_for("music_play", artist_name= artist_name, track_name = track_name,
                                 album_name = album_name, mode='library')
        strm_file.write(content)
        strm_file.close()

    return changed

def setup_library(library_folder):
    if library_folder[-1] != "/":
        library_folder += "/"

    if not xbmcvfs.exists(library_folder):
        # create folder
        xbmcvfs.mkdir(library_folder)

    # return translated path
    return xbmc.translatePath(library_folder)