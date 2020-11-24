"""
Reads
"""
import argparse
import configparser
import re

import challonge
import util_challonge

def extract_tourney_num(tourney_id):
    """Extract the numbers at the end of tournament series."""
    m = re.search(r'(\d+)$', tourney_id)
    return int(m.group(1))

# Get config file from args.
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ini', default='create_next.ini',
                    help='config file to read from')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.ini)
latest_url = config['Settings']['latest_tournament_url']
user = config['Settings']['user']
api_key = config['Settings']['api_key']
tourney_id = util_challonge.extract_tourney_name(latest_url)

challonge.set_credentials(user, api_key)
# Parameters to copy from previous tournament.
parameters = challonge.tournaments.show(tourney_id)
important_keys = {
    'name', 'tournament_type', 'url', 'subdomain', 'description',
    'open_signup', 'hold_third_place_match', 'pts_for_match_win',
    'pts_for_match_tie', 'pts_for_game_win', 'pts_for_game_tie',
    'pts_for_bye', 'swiss_rounds', 'ranked_by', 'rr_pts_for_match_win',
    'rr_pts_for_match_tie', 'rr_pts_for_game_win', 'rr_pts_for_game_tie',
    'accept_attachments', 'hide_forum', 'show_rounds', 'private',
    'notify_users_when_matches_open',
    'notify_users_when_the_tournament_ends', 'sequential_pairings',
    'signup_cap', 'check_in_duration', 'grand_finals_modifier',
}

parameters = {k:parameters[k] for k in parameters
              if k in important_keys}
# Increment the tournament's number.
number = extract_tourney_num(tourney_id)
name = re.sub(str(number), str(number+1), parameters['name'])
url = re.sub(str(number), str(number+1), parameters['url'])
tourney_id = re.sub(str(number), str(number+1), tourney_id)

del parameters['name']
del parameters['url']

challonge.tournaments.create(
    name,
    url,
    **parameters
)

full_url = util_challonge.tourney_name_to_url(tourney_id)
print('Created tournament {}'.format(full_url))

# Update the .ini file with the new tournament URL.
config['Settings']['latest_tournament_url'] = full_url
with open(args.ini, 'w') as f:
    config.write(f)
