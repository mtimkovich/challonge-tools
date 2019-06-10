from flask import Blueprint, render_template, abort, jsonify, request
import json

import auTO

auto = Blueprint('auTO', __name__)

@auto.route('/')
def index():
    return 'TODO: Load Vue page'

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
                'in_progress': obj.in_progress,
                'suggested_play_order': obj.suggested_play_order,
            }
        else:
            return json.JSONEncoder.default(self, obj)

@auto.route('/api/get_matches', methods=['POST'])
def get_matches():
    url = request.form.get('url')
    # TODO: Get Challonge login info.
    # TODO: Pass in authorization to auTO.
    to = auTO.auTO(url)

    return jsonify(to.open_matches, cls=MatchEncoder)

@auto.route('/api/report', methods=['POST'])
def report():
    pass
