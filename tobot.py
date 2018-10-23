#!/usr/bin/env python
import challonge
import subprocess
import sys
import time

import util_challonge


config_file = '../challonge.ini'
initialized = util_challonge.set_challonge_credentials_from_config(config_file)
if not initialized:
    sys.exit(1)

tourney_url = 'https://challonge.com/tobot_test'
tourney_name = util_challonge.extract_tourney_name(tourney_url)
# Cache participants so we only don't have to make a network call every time
# we want to get tags.
participants = challonge.participants.index(tourney_name)
matches = challonge.matches.index(tourney_name)
open_matches = []


def update_matches():
    global open_matches
    matches = challonge.matches.index(tourney_name)
    match_infos = [MatchInfo(m) for m in matches]
    # Sort matches by suggested play order
    open_matches = sorted(m for m in match_infos if m.state == 'open')

def player_tag_from_id(id):
    """
    Get the player tag, given a player ID.

    O(n)

    @param id (int): Player ID.
    returns: display name
    """
    for p in participants:
        if p['id'] == id:
            return p['display_name']
    raise ValueError('No player with id: {}'.format(id))


class MatchInfo(object):
    """
    TODO: Mark match as in progress.
        * the challonge API doesn't support, so we'll need to store a local
              store of what matches are in progress.
    TODO: Report scores.
    """
    def __init__(self, match):
        self.match_id = match['id']
        self.id1 = match['player1_id']
        self.id2 = match['player2_id']
        self.state = match['state']
        self.suggested_play_order = match['suggested_play_order']
        self.identifier = match['identifier']
        self.underway_at = match['underway_at']

        if self.state == 'open':
            self.player1_tag = player_tag_from_id(self.id1)
            self.player2_tag = player_tag_from_id(self.id2)

    def identifier_str(self):
        """The match identifier with an * if it's in progress."""
        underway = ' '
        if self.underway_at is not None:
            underway = '*'

        return '{}{}:'.format(underway, self.identifier)

    def __repr__(self):
        return '{}{}: {} vs {}'.format(self.identifier_str(),
                                     self.identifier,
                                     self.player1_tag,
                                     self.player2_tag)

    def _parts(self):
        return [self.identifier_str(),
                self.player1_tag,
                'vs',
                self.player2_tag]

    def __lt__(self, other):
        return self.suggested_play_order < other.suggested_play_order


def column_print_matches(match_infos):
    """Print match info in nice pretty columns."""
    rows = [m._parts() for m in match_infos]
    widths = [max(map(len, col)) for col in zip(*rows)]
    for row in rows:
        print(" ".join((val.ljust(width) for val, width in zip(row, widths))))


def nop():
    pass


def prompt():
    def help_prompt():
        for cmd, help in commands.items():
            print('  {} - {}'.format(cmd, help[0]))

    commands = {
        'u': ('update match list', update_matches),
        'h': ('print help', help_prompt),
        '?': ('print help', help_prompt),
        'q': ('quit', sys.exit),
        '*': ('toggle in progress status', nop),
        'r': ('report the result of a match. e.g. `r I 2-0`', nop),
    }

    ch = input('> ').lower()
    if ch in commands:
        commands[ch][1]()
    else:
        print('invalid command: {}'.format(ch))
    print()


while True:
    update_matches()

    column_print_matches(open_matches)
    prompt()
