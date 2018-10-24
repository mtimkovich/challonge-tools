#!/usr/bin/env python
"""
TO Bot simplifies the running of Challonge brackets by showing a queue to
call matches, and provides a CLI to update the bracket.
"""
import argparse
import challonge
import re
import readline
import sys

import defaults
import util_challonge


VERSION = 'v0.3'
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

initialized = util_challonge.set_challonge_credentials_from_config(
                args.config_file)
if not initialized:
    sys.exit(1)

tourney_name = util_challonge.extract_tourney_name(args.tourney_url)
# Cache participants so we only don't have to make a network call every time
# we want to get tags.
participants = challonge.participants.index(tourney_name)
open_matches = []
in_progress_map = {}


def update_matches():
    """Get the latest match data from Challonge."""
    matches = challonge.matches.index(tourney_name)
    match_infos = [MatchInfo(m) for m in matches]

    # Sort matches by suggested play order
    global open_matches
    open_matches = sorted(m for m in match_infos if m.state == 'open')

    # Set in progress based on our stored values.
    for m in open_matches:
        m.underway_at = in_progress_map.get(m.identifier, m.underway_at)

    if len(matches) > 0 and len(open_matches) == 0:
        print('Tournament is completed!')


def player_tag(id):
    """
    Get the player tag, given a player ID.

    O(n)

    @param id (int): Player ID.
    returns: display name.
    """
    for p in participants:
        if p['id'] == id:
            return p['display_name']
    raise ValueError('No player with id: {}'.format(id))


class MatchInfo(object):
    """
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
        """The match identifier is prefixed with a * if it's in progress."""
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


def column_print(things):
    """
    Print in nice pretty columns.

    |things| must implement a ._parts() method.
    """
    rows = [m._parts() for m in things]
    widths = [max(map(len, col)) for col in zip(*rows)]
    for row in rows:
        print(" ".join((val.ljust(width) for val, width in zip(row, widths))))


def confirm(question):
    """Ask 'em my questions and get some answers."""
    return input(question + ' [Y/n] ').lower() in ['y', 'yes']


def get_match_from_identifier(identifier):
    for m in open_matches:
        if m.identifier == identifier:
            return m
    else:
        print('match {} not found.'.format(identifier))
        return None


def toggle_in_progress(args):
    if not args:
        print('* [match identifier]')
        return

    identifier = args[0].upper()
    match = get_match_from_identifier(identifier)

    if match.underway_at is None:
        match.underway_at = True
        in_progress_map[identifier] = True
    else:
        match.underway_at = None
        del in_progress_map[identifier]


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

    match = get_match_from_identifier(identifier)
    if match is None:
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

    yes = confirm('{} beat {} {}?'.format(player_tag(winner_id),
                                          player_tag(loser_id),
                                          print_score))
    if yes:
        challonge.matches.update(tourney_name, match.id, scores_csv=score,
                                 winner_id=winner_id)
        update_matches()


class Commander(object):
    """Object to hold all the beautiful commands."""
    def __init__(self, *cmds):
        self._commands = {}

        self.add(*cmds)

    def _add(self, cmd):
        self._commands[cmd.short] = cmd
        self._commands[cmd.long] = cmd

    def add(self, *cmds):
        for cmd in cmds:
            self._add(cmd)

    def __getitem__(self, key):
        return self._commands.get(key)

    def __contains__(self, item):
        return self[item] is not None

    def help_prompt(self):
        print('`A` represents the match identifier.')
        output = [cmd for key, cmd in
                  sorted(self._commands.items(), key=lambda d: d[1])
                  if len(key) == 1]
        column_print(output)


class Command(object):
    index = 0

    def __init__(self, short, long, help, func):
        self.short = short
        self.long = long
        self.help = help
        self.func = func
        self.index = Command.index
        Command.index += 1

    def _parts(self):
        return [' ', self.long, '({})'.format(self.short), ' ' + self.help]

    def __lt__(self, other):
        return self.index < other.index


commander = Commander(
    Command('u', 'update', 'update match info', update_matches),
    Command('*', 'start', "toggle match's in progress status e.g. `start A`",
            toggle_in_progress),
    Command('r', 'report', 'report the result of a match e.g. `report A 2-0`',
            report),
)
commander.add(
    Command('h', 'help', 'print help', commander.help_prompt),
    Command('?', 'help', 'print help', commander.help_prompt),
    Command('q', 'quit', 'quit', sys.exit),
)


def prompt():
    """The main user interaction loop."""
    user = input('> ').lower()
    if user:
        split = user.split(' ')
        ch = split[0]
        if ch in commander:
            if len(split) == 1:
                commander[ch].func()
            else:
                commander[ch].func(split[1:])
        else:
            print('invalid command: {}'.format(ch))
            commander.help_prompt()
    else:
        commander.help_prompt()

    print()


update_matches()
while True:
    column_print(open_matches)
    prompt()
