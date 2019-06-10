from flask import Blueprint, render_template, abort, jsonify, request
import json

from auTO

auto = Blueprint('auTO', __name__)

@auto.route('/'):
    # TODO: Load Vue page
    pass

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

@auto.route('/api/get_matches', method=['POST']):
    url = request.form.get('url')
    to = auTo.auTO(url)

    return jsonify(to.open_matches, cls=MatchEncoder)

@auto.route('/api/report', method=['POST']):
    pass
