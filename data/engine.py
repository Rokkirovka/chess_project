from stockfish import Stockfish
from chess import Move
from data import db_session
from data.analyzes import Analysis
import platform


def engine_move(fen, level):
    if platform.system() == 'Windows':
        engine = Stockfish('stockfish_win/stockfish-windows-x86-64-avx2.exe')
    else:
        engine = Stockfish('stockfish_lin/stockfish-windows-x86-64-avx2.exe')
    engine.set_fen_position(fen)
    engine.set_skill_level(level * 2)
    engine.set_depth(15)
    move = engine.get_best_move()
    return Move.from_uci(move)


def engine_analysis(fen, depth):
    db_sess = db_session.create_session()
    analysis = db_sess.query(Analysis).filter(Analysis.fen == str(fen)).first()
    if analysis and analysis.depth >= int(depth):
        score = analysis.score
        depth = analysis.depth
    else:
        if platform.system() == 'Windows':
            engine = Stockfish('stockfish_win/stockfish-windows-x86-64-avx2.exe')
        else:
            engine = Stockfish('stockfish_lin/stockfish-windows-x86-64-avx2.exe')
        engine.set_fen_position(fen)
        engine.set_depth(depth)
        info = engine.get_evaluation()
        if info['type'] == 'cp':
            score = info['value'] / 100
        else:
            score = '#' + str(info['value'])
        if analysis is None:
            analysis = Analysis()
        analysis.depth = depth
        analysis.score = score
        analysis.fen = fen
        db_sess.add(analysis)
        db_sess.commit()
    db_sess.close()
    return {'score': score, 'depth': int(depth)}
