"""A simple program for exporting your library from gmusic."""
from __future__ import print_function
import os.path
import json
from getpass import getpass
from gmusicapi.clients import Mobileclient, Musicmanager


KEYS = ['comment', 'rating', 'composer', 'year', 'album',
        'albumArtist', 'title', 'totalDiscCount', 'trackNumber',
        'discNumber', 'totalTrackCount', 'estimatedSize',
        'beatsPerMinute', 'genre', 'playCount', 'artist',
        'durationMillis']


def select_keys(d, keys):
    """Return a dict that is a subset of d with only
    the keys specified. Any keys that do not exist in
    d are set to None in the returned dict.

    """
    return {key : d.get(key) for key in keys}


def login():
    """Login with oauth. This is required for Musicmanager."""
    manager = Musicmanager()
    path = os.path.expanduser('~/.accessall')
    if os.path.isfile(path):
        creds = path
    else:
        creds = manager.perform_oauth(storage_filepath=path)
    manager.login(oauth_credentials=creds)
    return manager


def exportlib(user, password):
    """Logs into Google Music and exports the user's
    library to a file called 'export.json'.

    """
    client = Mobileclient()
    client.login(user, password)
    with open('export.json', 'w+') as out:
        for songs in client.get_all_songs(incremental=True):
            for song in songs:
                pruned = select_keys(song, KEYS)
                print(json.dumps(pruned), file=out)


def find_song(manager, song, artist, album):
    for songs in manager.get_uploaded_songs(incremental=True):
        for songh in songs:
            match = (
                songh.get('title') == song
                and songh.get('artist') == artist
                and songh.get('album') == album
                )
            if match:
                return songh['id']


def download(manager, song, artist, album):
    id = find_song(manager, song, artist, album)
    if id:
        name, stream = manager.download_song(id)
        print('Writing', name)
        with open(name, 'wb') as f:
            f.write(stream)
    else:
        print('Song not found.')


def main(args):
    """Program entry point."""
    if args['export']:
        password = getpass('Password for Google Music: ')
        exportlib(args['USER'], password)
    elif args['download']:
        download(login(), args['SONG'], args['ARTIST'], args['ALBUM'])
