#!/usr/bin/env python
"""
auTO simplifies the running of Challonge brackets by showing a queue to
call matches, and provides a CLI to update the bracket.
"""
import argparse
import challonge
import re
import readline
import sys

import defaults
import util_challonge


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
    ans = input(question + ' [Y/n] ').lower()
    if ans:
        # Don't store this input in history.
        readline.remove_history_item(
            readline.get_current_history_length()-1)
    return ans in ['y', 'yes']


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


class MatchInfo(object):
    """
    TODO: Keep track of available setups.
    """
    def __init__(self, match, participants):
        self.id = match['id']
        self.player1_id = match['player1_id']
        self.player2_id = match['player2_id']
        self.state = match['state']
        self.suggested_play_order = match['suggested_play_order']
        self.identifier = match['identifier']

        self.in_progress = match['underway_at'] is not None
        self.participants = participants

        if self.state == 'open':
            self.player1_tag = self.player_tag(self.player1_id)
            self.player2_tag = self.player_tag(self.player2_id)

    def player_tag(self, id):
        """
        Get the player tag, given a player ID.

        O(n)

        @param id (int): Player ID.
        @param participants (list string): List of player infos.
        returns: display name.
        """
        for p in self.participants:
            if p['id'] == id:
                return p['display_name']
        raise ValueError('No player with id: {}'.format(id))

    def identifier_str(self):
        """The match identifier is prefixed with a * if it's in progress."""
        underway = ' '
        if self.in_progress:
            underway = '*'

        return '{}{}:'.format(underway, self.identifier)

    def _parts(self):
        return [self.identifier_str(),
                self.player1_tag,
                'vs',
                self.player2_tag]

    def __lt__(self, other):
        """Sort the unplayed matches before the the in progress ones."""
        return ((self.in_progress, self.suggested_play_order)
                < (other.in_progress, other.suggested_play_order))

class auTO(object):
    def __init__(self, tourney_url):
        self.tourney_name = util_challonge.extract_tourney_name(tourney_url)
        # Cache participants so we only don't have to make a network call
        # every time we want to get tags.
        self.participants = challonge.participants.index(self.tourney_name)
        self.in_progress_map = {}
        self.update_matches()

        self.commands = Commander(
            Command('u', 'update', 'update match info', self.update_matches),
            Command('*', 'start',
                    "toggle match's in progress status e.g. `start A`",
                    self.toggle_in_progress),
            Command('r', 'report',
                    'report the result of a match e.g. `report A 2-0`',
                    self.report),
        )
        self.commands.add(
            Command('h', 'help', 'print help', self.commands.help_prompt),
            Command('?', 'help', 'print help', self.commands.help_prompt),
            Command('q', 'quit', 'quit', sys.exit),
        )

    def update_matches(self):
        """Get the latest match data from Challonge."""
        matches = challonge.matches.index(self.tourney_name)
        match_infos = [MatchInfo(m, self.participants) for m in matches]

        # Set in progress based on our stored values.
        for m in match_infos:
            m.in_progress = self.in_progress_map.get(m.identifier,
                                                     m.in_progress)

        self.open_matches = sorted(m for m in match_infos if m.state == 'open')

        if len(matches) > 0 and len(self.open_matches) == 0:
            print('Tournament is completed!')

    def print_open_matches(self):
        self.open_matches = sorted(self.open_matches)
        column_print(self.open_matches)

    def get_match_from_identifier(self, identifier):
        for m in self.open_matches:
            if m.identifier == identifier:
                return m
        else:
            print('match {} not found.'.format(identifier))
            return None

    def toggle_in_progress(self, args):
        if not args:
            print('* [match identifier]')
            return

        identifier = args[0].upper()
        match = self.get_match_from_identifier(identifier)

        if match is None:
            return
        elif match.in_progress:
            match.in_progress = False
            del self.in_progress_map[identifier]
        else:
            match.in_progress = True
            self.in_progress_map[identifier] = True

    def report(self, args):
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

        match = self.get_match_from_identifier(identifier)
        if match is None:
            return

        score_val = score.split('-')
        print_score = score
        if score_val[0] > score_val[1]:
            winner_id = match.player1_id
            loser_id = match.player2_id
        elif score_val[0] < score_val[1]:
            winner_id = match.player2_id
            loser_id = match.player1_id
            print_score = print_score[::-1]
        else:
            print("A tie? I don't think so.")
            return

        yes = confirm('{} beat {} {}?'.format(match.player_tag(winner_id),
                                              match.player_tag(loser_id),
                                              print_score))
        if yes:
            challonge.matches.update(self.tourney_name, match.id,
                                     scores_csv=score, winner_id=winner_id)
            self.update_matches()

    def prompt(self):
        """The main user interaction loop."""
        user = input('> ').lower()
        if not user:
            self.commands.help_prompt()
            print()
            return

        split = user.split(' ')
        ch = split[0]

        if ch not in self.commands:
            print('invalid command: {}'.format(ch))
            self.commands.help_prompt()
            print()
            return

        if len(split) == 1:
            self.commands[ch].func()
        else:
            self.commands[ch].func(split[1:])
        print()


if __name__ == '__main__':
    VERSION = 'v0.7'
    parser = argparse.ArgumentParser(
                description='auTO ' + VERSION,
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

    # Initialize auTO
    auto = auTO(args.tourney_url)

    while True:
        auto.print_open_matches()
        auto.prompt()
