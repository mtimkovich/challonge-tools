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
# Cache participants so we only don't have to make a network call everytime
# we want to get tags.
participants = challonge.participants.index(tourney_name)


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
    def __init__(self, match):
        self.id1 = match['player1_id']
        self.id2 = match['player2_id']
        self.state = match['state']
        self.suggested_play_order = match['suggested_play_order']
        self.identifier = match['identifier']
        self.underway_at = match['underway_at']

        if self.state == 'open':
            self.player1_tag = player_tag_from_id(self.id1)
            self.player2_tag = player_tag_from_id(self.id2)

    def __repr__(self):
        underway = ' '
        if self.underway_at is not None:
            underway = '*'
        return '{}{}: {} vs {}'.format(underway,
                                     self.identifier,
                                     self.player1_tag,
                                     self.player2_tag)

    def _parts(self):
        underway = ' '
        if self.underway_at is not None:
            underway = '*'
        return [underway+self.identifier+':',
                self.player1_tag,
                'vs',
                self.player2_tag]


def column_print_matches(match_infos):
    PADDING = 1
    rows = [m._parts() for m in match_infos]
    widths = [max(map(len, col)) for col in zip(*rows)]
    for row in rows:
        print(" ".join((val.ljust(width) for val, width in zip(row, widths))))


while True:
    matches = challonge.matches.index(tourney_name)
    match_infos = [MatchInfo(m) for m in matches]
    open_matches = [m for m in match_infos if m.state == 'open']

    # Clear screen
    subprocess.call(['clear'])

    column_print_matches(open_matches)

    time.sleep(5)
