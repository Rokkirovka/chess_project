from stockfish import Stockfish
from chess import Move


def engine_move(fen, level):
    engine = Stockfish('stockfish/stockfish-windows-x86-64-avx2.exe')
    engine.set_fen_position(fen)
    engine.set_skill_level(level * 2)
    engine.set_depth(15)
    move = engine.get_best_move()
    return Move.from_uci(move)


def engine_analysis(fen):
    engine = Stockfish('stockfish/stockfish-windows-x86-64-avx2.exe')
    engine.set_fen_position(fen)
    engine.set_depth(15)
    info = engine.get_evaluation()
    if info['type'] == 'cp':
        score = info['value'] / 100
    else:
        score = '#' + str(info['value'])
    return score
