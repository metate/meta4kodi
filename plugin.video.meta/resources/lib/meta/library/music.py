import os
import shutil
import requests
import sqlite3
import glob
import re

from xbmcswift2 import xbmc, xbmcvfs

from meta import plugin
from meta.utils.text import to_utf8
from lastfm import lastfm
from meta.gui import dialogs


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

    track_info = lastfm.get_track_info(artist_name, track_name)
    if "album" in track_info:
        track_number = track_info["album"]["@attr"]["position"]
        nfo_track_path = os.path.join(album_folder, "{0} {1}.nfo".format(track_number, track_name))
    else:
        track_number = ""
        nfo_track_path = os.path.join(album_folder, track_name + ".nfo")

    if not xbmcvfs.exists(nfo_track_path):
        changed = True
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
    if "album" in track_info:
        track_number = track_info["album"]["@attr"]["position"]
        strm_filepath = os.path.join(album_folder, "{0} {1}.strm".format(track_number, track_name))
    else:
        strm_filepath = os.path.join(album_folder, track_name + ".strm")
    if not xbmcvfs.exists(strm_filepath):
        changed = True
        track_info = lastfm.get_track_info(artist_name, track_name)
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

def get_pathId(dirName):
    dialogs.ok("getting pathid", repr(dirName))
    absDirName = os.path.abspath(dirName) + os.sep
    absDirName = absDirName.replace('kodi', 'Kodi')
    c.execute("SELECT * FROM path WHERE strPath = ?", (absDirName,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        return None


def get_albumId(album, artist):
    c.execute("SELECT * FROM album WHERE strAlbum = ? AND strArtists = ?", (album, artist))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO album (strAlbum,strArtists,strReleaseType) VALUES (?,?,?)", (album, artist, "album"))
        id = c.lastrowid
        conn.commit()
        return id


def get_artistId(artist):
    c.execute("SELECT * FROM artist WHERE strArtist = ?", (artist,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO artist (strArtist) VALUES (?)", (artist,))
        id = c.lastrowid
        conn.commit()
        return id


def get_songId(albumId, pathId, artist, song, filename):
    c.execute("SELECT * FROM song WHERE idAlbum = ? AND idPath = ? And strArtists = ? AND strTitle = ?",
              (albumId, pathId, artist, song))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO song (idAlbum, idPath, strArtists, strTitle, strFilename) VALUES (?,?,?,?,?)",
                  (albumId, pathId, artist, song, filename))
        id = c.lastrowid
        conn.commit()
        return id


def add_albumArtist(albumId, artistId, artist):
    c.execute("SELECT * FROM album_artist WHERE idArtist = ? AND idAlbum = ?", (artistId, albumId))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO album_artist (idArtist, idAlbum, strArtist) VALUES (?,?,?)", (artistId, albumId, artist))


def add_songArtist(songId, artistId, artist):
    c.execute("SELECT * FROM song_artist WHERE idArtist = ? AND idSong = ?", (artistId, songId))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO song_artist (idArtist, idSong, strArtist) VALUES (?,?,?)", (artistId, songId, artist))


def add_folder_to_music_database(music_folder):
    dialogs.ok("adding music", "testing")
    setup_database_connection()
    music_folder = xbmc.translatePath(music_folder)  # translate from special:// to absolute
    dialogs.ok("adding music", repr(music_folder))
    for dirName, subdirList, fileList in os.walk(music_folder):
        pathId = get_pathId(dirName)
        if not pathId:
            continue
        for fname in fileList:
            if fname.endswith("strm"):
                dirnameparts = dirName.split(os.sep)
                artist = dirnameparts[-2]
                album = dirnameparts[-1]
                song = fname.replace('.strm', '')
                artistId = get_artistId(artist)
                albumId = get_albumId(album, artist)
                add_albumArtist(albumId, artistId, artist)
                songId = get_songId(albumId, pathId, artist, song, fname)
                add_songArtist(songId, artistId, artist)
                conn.commit()


def setup_database_connection():
    global c
    global conn
    # set up sqlite connection
    path = xbmc.translatePath('special://home/userdata/Database')
    files = glob.glob(os.path.join(path, 'MyMusic*.db'))
    ver = 0
    dbPath = ''

    # Find the highest version number of textures, it's always been textures13.db but you can never be too careful!
    for file in files:
        dbversion = int(re.compile('MyMusic(.+?).db').findall(file)[0])
        if ver < dbversion:
            ver = dbversion
            dbPath = file

    db = xbmc.translatePath(dbPath)
    conn = sqlite3.connect(db, timeout=10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    conn.text_factory = str
    c = conn.cursor()
    c.row_factory = sqlite3.Row


def get_albumId(album, artist):
    c.execute("SELECT * FROM album WHERE strAlbum = ? AND strArtists = ?", (album, artist))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO album (strAlbum,strArtists,strReleaseType) VALUES (?,?,?)", (album, artist, "album"))
        id = c.lastrowid
        conn.commit()
        return id


def get_artistId(artist):
    c.execute("SELECT * FROM artist WHERE strArtist = ?", (artist,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO artist (strArtist) VALUES (?)", (artist,))
        id = c.lastrowid
        conn.commit()
        return id


def get_songId(albumId, pathId, artist, song, filename):
    c.execute("SELECT * FROM song WHERE idAlbum = ? AND idPath = ? And strArtists = ? AND strTitle = ?",
              (albumId, pathId, artist, song))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO song (idAlbum, idPath, strArtists, strTitle, strFilename) VALUES (?,?,?,?,?)",
                  (albumId, pathId, artist, song, filename))
        id = c.lastrowid
        conn.commit()
        return id


def add_albumArtist(albumId, artistId, artist):
    c.execute("SELECT * FROM album_artist WHERE idArtist = ? AND idAlbum = ?", (artistId, albumId))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO album_artist (idArtist, idAlbum, strArtist) VALUES (?,?,?)", (artistId, albumId, artist))


def add_songArtist(songId, artistId, artist):
    c.execute("SELECT * FROM song_artist WHERE idArtist = ? AND idSong = ?", (artistId, songId))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO song_artist (idArtist, idSong, strArtist) VALUES (?,?,?)", (artistId, songId, artist))


def add_folder_to_music_database(music_folder):
    setup_database_connection()
    for dirName, subdirList, fileList in os.walk(music_folder):
        dirName = xbmc.translatePath(dirName) # translate from special:// to absolute
        dialogs.ok("testing", repr(dirName))
        pathId = get_pathId(dirName)
        if not pathId:
            continue
        for fname in fileList:
            if fname.endswith("strm"):
                dirnameparts = dirName.split(os.sep)
                artist = dirnameparts[-2]
                album = dirnameparts[-1]
                song = fname.replace('.strm', '')
                artistId = get_artistId(artist)
                albumId = get_albumId(album, artist)
                add_albumArtist(albumId, artistId, artist)
                songId = get_songId(albumId, pathId, artist, song, fname)
                add_songArtist(songId, artistId, artist)
                conn.commit()

def setup_database_connection():
    global c
    global conn
    # set up sqlite connection
    path = xbmc.translatePath('special://home/userdata/Database')
    files = glob.glob(os.path.join(path, 'MyMusic*.db'))
    ver = 0
    dbPath = ''

    # Find the highest version number of textures, it's always been textures13.db but you can never be too careful!
    for file in files:
        dbversion = int(re.compile('MyMusic(.+?).db').findall(file)[0])
        if ver < dbversion:
            ver = dbversion
            dbPath = file

    db = xbmc.translatePath(dbPath)
    conn = sqlite3.connect(db, timeout=10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    conn.text_factory = str
    c = conn.cursor()
    c.row_factory = sqlite3.Row
