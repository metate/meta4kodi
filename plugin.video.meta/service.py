#!/usr/bin/python
# -*- coding: utf-8 -*-
if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import datetime
import sqlite3
import glob
import re

from xbmcswift2 import xbmc
from meta import plugin
from meta.video_player import VideoPlayer
from meta.utils.properties import get_property, clear_property
from lastfm import lastfm
from meta.gui import dialogs
from addon import update_library
from settings import UPDATE_LIBRARY_INTERVAL, SETTING_MUSIC_LIBRARY_FOLDER

player = VideoPlayer()

class Monitor(xbmc.Monitor):
    def onDatabaseUpdated(self, database):
        if database == "video":
            if get_property("clean_library"):
                xbmc.executebuiltin("XBMC.CleanLibrary(video, false)")
                clear_property("clean_library")
        if database == "music":
            # need to manualy change the database file to add strm files to it
            music_directory = plugin.get_setting(SETTING_MUSIC_LIBRARY_FOLDER)
            self.add_folder_to_music_database(music_directory)

    def get_pathId(self,dirName):
        absDirName = os.path.abspath(dirName) + os.sep
        absDirName = absDirName.replace('kodi', 'Kodi')
        c.execute("SELECT * FROM path WHERE strPath = ?", (absDirName,))
        row = c.fetchone()
        if row:
            return row[0]
        else:
            return None

    def get_albumId(self,album, artist):
        c.execute("SELECT * FROM album WHERE strAlbum = ? AND strArtists = ?", (album, artist))
        row = c.fetchone()
        if row:
            return row[0]
        else:
            c.execute("INSERT INTO album (strAlbum,strArtists,strReleaseType) VALUES (?,?,?)", (album, artist, "album"))
            id = c.lastrowid
            conn.commit()
            return id

    def get_artistId(self, artist):
        c.execute("SELECT * FROM artist WHERE strArtist = ?", (artist,))
        row = c.fetchone()
        if row:
            return row[0]
        else:
            c.execute("INSERT INTO artist (strArtist) VALUES (?)", (artist,))
            id = c.lastrowid
            conn.commit()
            return id

    def get_songId(self, albumId, pathId, artist, song, song_number, filename):
        c.execute("SELECT * FROM song WHERE idAlbum = ? AND idPath = ? And strArtists = ? AND strTitle = ?",
                  (albumId, pathId, artist, song))
        row = c.fetchone()
        if row:
            return row[0]
        else:
            c.execute("INSERT INTO song (idAlbum, idPath, strArtists, strTitle, itrack, strFilename) VALUES (?,?,?,?,?,?)",
                      (albumId, pathId, artist, song, song_number, filename))
            id = c.lastrowid
            conn.commit()
            return id

    def add_albumArtist(self, albumId, artistId, artist):
        c.execute("SELECT * FROM album_artist WHERE idArtist = ? AND idAlbum = ?", (artistId, albumId))
        row = c.fetchone()
        if not row:
            c.execute("INSERT INTO album_artist (idArtist, idAlbum, strArtist) VALUES (?,?,?)",
                      (artistId, albumId, artist))

    def add_songArtist(self, songId, artistId, artist):
        c.execute("SELECT * FROM song_artist WHERE idArtist = ? AND idSong = ?", (artistId, songId))
        row = c.fetchone()
        if not row:
            c.execute("INSERT INTO song_artist (idArtist, idSong, strArtist) VALUES (?,?,?)",
                      (artistId, songId, artist))

    def add_folder_to_music_database(self, music_folder):
        self.setup_database_connection()
        music_folder = xbmc.translatePath(music_folder)  # translate from special:// to absolute
        for dirName, subdirList, fileList in os.walk(music_folder):
            pathId = self.get_pathId(dirName)
            if not pathId:
                continue
            for fname in fileList:
                if fname.endswith("strm"):
                    dirnameparts = dirName.split(os.sep)
                    artist = dirnameparts[-2]
                    album = dirnameparts[-1]
                    song = fname.replace('.strm', '')
                    song_regex = re.compile("(\d+)* (.*)")
                    song_number = re.sub(song_regex, r"\1", song)
                    song = re.sub(song_regex, r"\2", song)

                    artistId = self.get_artistId(artist)
                    albumId = self.get_albumId(album, artist)
                    self.add_albumArtist(albumId, artistId, artist)
                    songId = self.get_songId(albumId, pathId, artist, song, song_number, fname)
                    self.add_songArtist(songId, artistId, artist)
                    conn.commit()

    def setup_database_connection(self):
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
                
monitor = Monitor()

def go_idle(duration):
    while not xbmc.abortRequested and duration > 0:
        if player.isPlayingVideo():
            player.currentTime = player.getTime()
        xbmc.sleep(1000)
        duration -= 1

def future(seconds):
    return datetime.datetime.now() + datetime.timedelta(seconds=seconds)


def main():
    go_idle(25)
    next_update = future(0)
    while not xbmc.abortRequested:
        if next_update <= future(0):
            next_update = future(UPDATE_LIBRARY_INTERVAL)
            update_library()
        go_idle(30*60)

if __name__ == '__main__':
    main()