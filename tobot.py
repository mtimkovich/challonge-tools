#!/usr/bin/env python
import argparse
import challonge
import re
import readline
import sys

import defaults
import util_challonge


VERSION = 'v0.2'
parser = argparse.ArgumentParser(description='TO Bot ' + VERSION,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "tourney_url",
    help="the URL of the tourney")
parser.add_argument(
    "--config_file",
    default=defaults.DEFAULT_CONFIG_FILENAME,
    help="the config file to read your Challonge credentials from")
args = parser.parse_args()

initialized = util_challonge.set_challonge_credentials_from_config(args.config_file)
if not initialized:
    sys.exit(1)

tourney_name = util_challonge.extract_tourney_name(args.tourney_url)
# Cache participants so we only don't have to make a network call every time
# we want to get tags.
participants = challonge.participants.index(tourney_name)
matches = challonge.matches.index(tourney_name)
open_matches = []


def update_matches():
    """Get the latest match data from Challonge."""
    # TODO: Do a 'merge' on in progress status instead of overwriting.
    global open_matches
    matches = challonge.matches.index(tourney_name)
    match_infos = [MatchInfo(m) for m in matches]
    # Sort matches by suggested play order
    open_matches = sorted(m for m in match_infos if m.state == 'open')


def player_tag(id):
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
        * The Challonge API doesn't support this, so we'll need to store a
            local store of what matches are in progress.
    TODO: Keep track of available setups.
    """
    def __init__(self, match):
        self.id = match['id']
        self.player1_id = match['player1_id']
        self.player2_id = match['player2_id']
        self.state = match['state']
        self.suggested_play_order = match['suggested_play_order']
        self.identifier = match['identifier']
        self.underway_at = match['underway_at']

        if self.state == 'open':
            self.player1_tag = player_tag(self.player1_id)
            self.player2_tag = player_tag(self.player2_id)

    def identifier_str(self):
        """The match identifier with an * if it's in progress."""
        underway = ' '
        if self.underway_at is not None:
            underway = '*'

        return '{}{}:'.format(underway, self.identifier)

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


class Command(object):
    def __init__(self, help, func):
        self.help = help
        self.func = func


def nop(args):
    print("This feature isn't implemented yet.")


def confirm(question):
    """Ask 'em my questions and get some answers."""
    return input(question + ' [Y/n] ').lower() in ['y', 'yes']


def report(args):
    """Report at match's result."""
    help_txt = 'r [match identifier] [player 1 score]-[player 2 score]'
    if len(args) != 2:
        print(help_txt)
        return

    identifier = args[0].upper()
    score = args[1]

    if not re.match(r'\d-\d', score):
        print(help_txt)
        return

    match = None
    for m in open_matches:
        if m.identifier == identifier:
            match = m
            break
    else:
        print('match {} not found.'.format(identifier))
        return

    score_val = score.split('-')
    print_score = score
    if score_val[0] > score_val[1]:
        winner_id = match.player1_id
        loser_id = match.player2_id
    else:
        winner_id = match.player2_id
        loser_id = match.player1_id
        print_score = print_score[::-1]

    yes = confirm('{} beat {} {}, correct?'.format(player_tag(winner_id),
                                                   player_tag(loser_id),
                                                   print_score))
    if yes:
        challonge.matches.update(tourney_name, match.id, scores_csv=score,
                                 winner_id=winner_id)
        update_matches()


def prompt():
    """The main user interaction loop."""
    def help_prompt():
        print('`A` represents the match identifier.')
        for ch, cmd in commands.items():
            print('  {} - {}'.format(ch, cmd.help))

    commands = {
        'u': Command('update match list', update_matches),
        '*': Command("toggle match's in progress status e.g. `* A`", nop),
        'r': Command('report the result of a match e.g. `r A 2-0`', report),
        'h': Command('print help', help_prompt),
        '?': Command('print help', help_prompt),
        'q': Command('quit', sys.exit),
    }

    user = input('> ').lower()
    if user:
        ch = user[0]
        if ch in commands:
            if len(user) == 1:
                commands[ch].func()
            else:
                commands[ch].func(user.split(' ')[1:])
        else:
            print('invalid command: {}'.format(ch))
            help_prompt()
    else:
        help_prompt()

    print()


update_matches()
while True:
    column_print_matches(open_matches)
    prompt()
