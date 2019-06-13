from flask import Blueprint, abort, jsonify, request, session, make_response
from flask_cors import CORS
import json

import auTO
# import challonge
import util_challonge

auto = Blueprint('auTO', __name__)
CORS(auto, resources={r'/*': {'origins': '*'}})

@auto.route('/')
def index():
    return 'TODO: return Vue page'

class MatchEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, auTO.MatchInfo):
            return {
                'id': obj.id,
                'player1_id': obj.player1_id,
                'player2_id': obj.player2_id,
                'player1_tag': obj.player1_tag,
                'player2_tag': obj.player2_tag,
                'state': obj.state,
                'in_progress': False,
                'round': obj.round,
                'suggested_play_order': obj.suggested_play_order,
            }
        else:
            return json.JSONEncoder.default(self, obj)

@auto.route('/api/get_matches', methods=['POST'])
def get_matches():
    url = request.get_json().get('url')
    # TODO: Use session.
    util_challonge.set_challonge_credentials_from_config('../challonge.ini')
    to = auTO.auTO(url)

    data = json.dumps(to.open_matches, cls=MatchEncoder)
    resp = make_response(data)
    resp.mimetype = 'application/json'

    return resp

@auto.route('/api/report', methods=['POST'])
def report():
    pass
