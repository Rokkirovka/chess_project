import datetime
from random import choice

import chess.engine
from chess import Move
from flask import Flask, render_template, request, redirect, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_socketio import SocketIO

from data import db_session
from data.chess_to_html import HTMLBoard
from data.games import Game
from data.rating_calculator import rating_calculation
from data.users import User
from forms.user import RegisterForm, GameForm, LoginForm, GameEngineForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)


def main():
    db_session.global_init('db/chess.db')
    app.run(host='0.0.0.0', port=80)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/create_game', methods=['GET', 'POST'])
@login_required
def new_game():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    game = Game()
    color = choice(['1', '2'])
    if color == '1':
        game.white_player = user.id
    else:
        game.black_player = user.id
    game.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    game.is_finished = False
    game.moves = ''
    game.type = 'friend'
    db_sess.add(game)
    db_sess.commit()
    game_id = str(game.id)
    db_sess.close()
    return redirect('/game/' + game_id)


@app.route('/fast_game', methods=['GET', 'POST'])
@login_required
def fast_game():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    game = db_sess.query(Game).filter(
        ((Game.black_player == int(user.id)) | (Game.white_player == int(user.id))) & (Game.type == 'fast')).filter(
        (Game.black_player == None) | (Game.white_player == None)).first()
    if not game:
        games = db_sess.query(Game).filter(
            ((Game.black_player == None) | (Game.white_player == None)) & (Game.type == 'fast')).all()
        if games:
            game = choice(games)
            print(game.white_player, game.black_player)
            if game.white_player is None:
                game.white_player = user.id
            else:
                game.black_player = user.id
            db_sess.commit()
            socketio.emit('reload')
        else:
            game = Game()
            color = choice(['1', '2'])
            if color == '1':
                game.white_player = user.id
            else:
                game.black_player = user.id
            game.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
            game.is_finished = False
            game.moves = ''
            game.type = 'fast'
            db_sess.add(game)
        db_sess.commit()
    game_id = str(game.id)
    db_sess.close()
    return redirect('/game/' + game_id)


@app.route('/create_engine_game', methods=['GET', 'POST'])
@login_required
def new_engine_game():
    form = GameEngineForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        opponent = db_sess.query(User).get(1)
        if not opponent:
            return render_template('create_game.html', form=form, message="Такого игрока нет")
        game = Game()
        if form.color.data == '3':
            color = choice(['1', '2'])
        else:
            color = form.color.data
        if color == '1':
            game.white_player = current_user.id
            game.black_player = opponent.id
        else:
            game.black_player = current_user.id
            game.white_player = opponent.id
        board = HTMLBoard()
        if color == '2':
            board.push(engine_move(board.fen()))
        db_sess.add(game)
        game.fen = board.fen()
        game.is_finished = False
        game.moves = ' '.join(move.uci() for move in board.move_stack)
        db_sess.commit()
        return redirect('/game/' + str(game.id))
    return render_template('create_engine_game.html', form=form)


@app.route('/game/<int:game_id>')
def play_game(game_id):
    db_sess = db_session.create_session()
    game = db_sess.query(Game).get(game_id)
    if game.white_player is None and game.black_player != current_user.id or game.black_player is None and game.white_player != current_user.id:
        if game.white_player is None:
            game.white_player = current_user.id
        else:
            game.black_player = current_user.id
        db_sess.commit()
        socketio.emit('reload')
    white_player = db_sess.query(User).get(game.white_player)
    black_player = db_sess.query(User).get(game.black_player)
    board = HTMLBoard(game.fen)
    board.current = game.cell
    board.move_stack = [Move.from_uci(move) for move in game.moves.split()]
    if request.is_json:
        if game.is_finished:
            dct = board.get_board_for_ajax()
            db_sess.close()
            return jsonify(dct)
        if (current_user.id == game.white_player and board.turn
                or current_user.id == game.black_player and not board.turn):
            cell = request.args.get('cell')
            board.add_cell(cell)
            game.cell = board.current
            check_position(board.fen(), game, white_player, black_player)
            if (game.white_player == 1 and board.turn or game.black_player == 1 and
                    not board.turn and not game.is_finished):
                board.push(engine_move(board.fen()))
            check_position(board.fen(), game, white_player, black_player)
            game.fen = board.fen()
            game.moves = ' '.join(move.uci() for move in board.move_stack)
            db_sess.commit()
            dct_for_socket = board.get_board_for_socket()
            dct_for_socket['result'] = game.result
            dct_for_socket['reason'] = game.reason
            dct_for_socket['end_game'] = game.is_finished
            socketio.emit('update_board', dct_for_socket)
        dct = board.get_board_for_ajax()
        if not (current_user.id == game.white_player and board.turn
                or current_user.id == game.black_player and not board.turn):
            dct = board.get_board_for_socket()
        db_sess.close()
        return jsonify(dct)
    lst = board.get_board()
    if current_user.is_authenticated:
        if current_user.id == game.white_player:
            role = 'white'
        elif current_user.id == game.black_player:
            role = 'black'
        else:
            role = 'spectator'
    else:
        role = 'spectator'
    db_sess.close()
    return render_template('game.html', board=lst, role=role,
                           white_player=white_player, black_player=black_player, end_game=game.is_finished,
                           result=game.result, reason=game.reason, turn=board.turn, type=game.type, url=request.url)


@app.route('/profile/<int:user_id>')
def profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    all_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) |
                                            (Game.white_player == int(user.id))) & (Game.is_finished == 1)).all()
    win_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) & (Game.result == 'Black win')) |
                                           ((Game.white_player == int(user.id)) & (Game.result == 'White win'))).all()
    draw_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) |
                                             (Game.white_player == int(user.id))) & (Game.result == 'Draw')).all()
    loose_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) & (Game.result == 'White win')) |
                                             ((Game.white_player == int(user.id)) & (Game.result == 'Black win'))).all()
    unfinished_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) |
                                                   (Game.white_player == int(user.id))) & (Game.is_finished == 0)).all()

    return render_template('profile.html', user=user,
                           all_games=all_games,
                           win_games=win_games,
                           draw_games=draw_games,
                           loose_games=loose_games,
                           unfinished_games=unfinished_games)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter((User.email == str(form.email.data)) |
                                      (User.nick == str(form.nick.data))).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.nick = form.nick.data
        user.email = form.email.data
        user.registration_date = datetime.datetime.now()
        user.set_password(form.password.data)
        user.rating = 1500
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
        db_sess.close()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == str(form.email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            db_sess.close()
            return redirect("/")
        db_sess.close()
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    db_sess.close()
    return user


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def check_position(fen, game, white_player, black_player):
    board = HTMLBoard(fen)
    if board.is_checkmate():
        game.reason = 'Checkmate'
        game.is_finished = 1
        if board.turn:
            game.result = 'Black win'
            wr = rating_calculation(white_player.rating, black_player.rating, 0)
            br = rating_calculation(black_player.rating, white_player.rating, 1)
        else:
            game.result = 'White win'
            wr = rating_calculation(white_player.rating, black_player.rating, 1)
            br = rating_calculation(black_player.rating, white_player.rating, 0)
        white_player.rating = wr
        black_player.rating = br
    if board.is_stalemate():
        game.is_finished = 1
        game.result = 'Draw'
        game.reason = 'Stalemate'
        wr = rating_calculation(white_player.rating, black_player.rating, 0.5)
        br = rating_calculation(black_player.rating, white_player.rating, 0.5)
        white_player.rating = wr
        black_player.rating = br


def engine_move(fen):
    board = HTMLBoard(fen)
    engine = chess.engine.SimpleEngine.popen_uci("data/stockfish/stockfish-windows-x86-64-avx2.exe")
    result = engine.play(board, chess.engine.Limit(time=0.1))
    engine.quit()
    return result.move


if __name__ == '__main__':
    main()
