"""A simple program for exporting your library from gmusic."""
from __future__ import print_function
import sys
import json
from getpass import getpass
from gmusicapi.clients import Mobileclient

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


def main():
    """Program entry point."""
    password = getpass('Password for Google Music: ')
    exportlib(sys.argv[1], password)
