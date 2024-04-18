from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.analyzes import Analysis
from flask import jsonify
from data.engine import engine_analysis


class AnalysisResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('fen', type=str)
        args = parser.parse_args()
        fen = args['fen']
        engine_analysis(fen)
        session = db_session.create_session()
        analysis = session.query(Analysis).filter(Analysis.fen == str(fen)).first()
        dct = analysis.to_dict(only=('best_move', 'fen', 'score'))
        session.close()
        return jsonify(dct)
