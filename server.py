import datetime
from random import choice, sample

from chess import Move, Board, square_name
from flask import Flask, render_template, request, redirect, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_restful import Api
from flask_socketio import SocketIO, join_room, leave_room, emit
from string import ascii_letters, digits

from data import chess_resources
from data import db_session
from data.engine import engine_move, engine_analysis
from data.games import Game
from data.users import User
from forms.user import RegisterForm, LoginForm, GameEngineForm
from data.rating_calculator import rating_calculation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_secret_key'
app.config['waiting'] = []
app.config['friendly'] = {}
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)
api.add_resource(chess_resources.AnalysisResource, '/api/analysis', endpoint='analysis')
api.add_resource(chess_resources.UserResource, '/api/user/<int:user_id>')
api.add_resource(chess_resources.UserListResource, '/api/users')
api.add_resource(chess_resources.GameResource, '/api/game/<int:game_id>')
api.add_resource(chess_resources.GameListResource, '/api/games')


def main():
    db_session.global_init('db/chess.db')
    app.run(host='0.0.0.0', port=80, debug=True)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Шахматы')


@socketio.on('append_fast_game')
def append_fast_game():
    db_sess = db_session.create_session()
    users = [user for user in app.config['waiting'] if abs(db_sess.get(User, user).rating - current_user.rating) < 200]
    if users:
        opponent = choice(users)
        if opponent != current_user.id:
            game = create_new_game(current_user.id, opponent, 'fast')
            game_id = game.id
            db_sess.close()
            app.config['waiting'].pop(app.config['waiting'].index(opponent))
            join_room(opponent)
            socketio.emit('start_game', game_id, room=opponent)
        else:
            join_room(current_user.id)
            db_sess.close()
    else:
        db_sess.close()
        app.config['waiting'].append(current_user.id)
        join_room(current_user.id)


@socketio.on('remove_fast_game')
def remove_fast_game():
    app.config['waiting'].remove(current_user.id)
    leave_room(current_user.id)


@socketio.on('append_friendly_game')
def append_friendly_game():
    token = ''.join(choice(ascii_letters + digits) for _ in range(8))
    app.config['friendly'][current_user.id] = token
    join_room(current_user.id)
    emit('friendly_game_url', request.host + '/friendly/' + token)


@socketio.on('remove_friendly_game')
def remove_friendly_game():
    del app.config['friendly'][current_user.id]
    leave_room(current_user.id)


@socketio.on('join_game')
def join_game(data):
    room_id = data['game_id']
    join_room(f'game_{room_id}')


@socketio.on('change_piece')
def change_piece(name):
    db_sess = db_session.create_session()
    user = db_sess.get(User, current_user.id)
    user.pieces = name
    db_sess.commit()
    db_sess.close()


@socketio.on('change_board')
def change_board(name):
    db_sess = db_session.create_session()
    user = db_sess.get(User, current_user.id)
    user.board = name
    db_sess.commit()
    db_sess.close()


@app.route('/friendly/<game_token>')
@login_required
def create_friendly_game(game_token):
    opponent = next((key for key, val in app.config['friendly'].items() if val == game_token), None)
    if opponent is None:
        return 'Not found'
    if opponent == current_user.id:
        return "You can't play with yourself"
    game = create_new_game(opponent, current_user.id, 'friendly')
    socketio.emit('start_game', game.id, room=opponent)
    return redirect(f'/game/{game.id}')


@app.route('/engine_game', methods=['GET', 'POST'])
def new_engine_game():
    fen = request.args['fen'] if 'fen' in request.args else ''
    color = request.args['color'] if 'color' in request.args else 'w'
    if request.is_json:
        data = request.args
        move = engine_move(data['new_fen'], data['level'])
        return jsonify({'from': square_name(move.from_square), 'to': square_name(move.to_square)})
    form = GameEngineForm()
    if form.validate_on_submit():
        if form.color.data == '3':
            role = choice(['w', 'b'])
        else:
            role = 'w' if form.color.data == '1' else 'b'
        return render_template('engine_game.html', level=form.level.data, fen=fen, role=role,
                               color=color, title='Игра с компьютером')
    return render_template('create_engine_game.html', form=form, color=color, title='Игра с компьютером')


@app.route('/game/<int:game_id>')
def play_game(game_id):
    db_sess = db_session.create_session()
    game = db_sess.get(Game, game_id)
    if game is None:
        return 'Not found'
    if request.is_json:
        data = request.args
        board = Board(game.fen)
        board.push(Move.from_uci(data['from'] + data['to']))
        game.fen = board.fen()
        game.moves = game.moves + ' ' + data['from'] + data['to']
        if board.is_game_over():
            socketio.emit('game_over', data=[*update_game(board, game)], room=f'game_{game_id}')
        db_sess.commit()
        socketio.emit('move', data, room=f'game_{game_id}')
        db_sess.close()
        return jsonify()
    white_player = db_sess.get(User, game.white_player)
    black_player = db_sess.get(User, game.black_player)
    if current_user.is_authenticated:
        if current_user.id == game.white_player:
            role = 'w'
        elif current_user.id == game.black_player:
            role = 'b'
        else:
            role = 's'
    else:
        role = 's'
    db_sess.close()
    return render_template('game.html', title='Игра', role=role, game=game, white_player=white_player,
                           black_player=black_player, end_game=game.is_finished, url=request.url)


@app.route('/analysis/<int:game_id>')
def analysis_game(game_id):
    db_sess = db_session.create_session()
    game = db_sess.get(Game, game_id)
    if game is None:
        return 'Not found'
    board = get_board_game(game)
    white_player = db_sess.get(User, game.white_player)
    black_player = db_sess.get(User, game.black_player)
    db_sess.close()
    if request.is_json:
        data = request.args
        score = engine_analysis(data['fen'], data['depth'])
        return jsonify(score)
    moves = [[square_name(move.from_square), square_name(move.to_square)] for move in board.move_stack]
    score = engine_analysis(board.fen(), 15)
    return render_template('analysis_game.html', title='Анализ',
                           white_player=white_player,
                           black_player=black_player,
                           reason=game.reason,
                           result=game.result,
                           moves=moves,
                           fen=game.fen,
                           score=score)


@app.route('/analysis')
def analysis_position():
    fen = request.args['fen'] if 'fen' in request.args else ''
    if request.is_json:
        data = request.args
        score = engine_analysis(data['fen'], data['depth'])
        return jsonify(score)
    return render_template('analysis_position.html', fen=fen, title='Анализ')


@app.route('/redactor')
def redactor():
    return render_template('redactor.html', title='Редактор доски')


@app.route('/profile/<int:user_id>')
def profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    if user is None:
        return 'Not found'
    user_games = db_sess.query(Game).filter(
        (Game.black_player == int(user.id)) | (Game.white_player == int(user.id))).all()
    wins = [game for game in user_games
            if game.result == '1-0' and game.white_player == user.id
            or game.result == '0-1' and game.black_player == user.id]
    looses = [game for game in user_games
              if game.result == '0-1' and game.white_player == user.id
              or game.result == '1-0' and game.black_player == user.id]
    draws = [game for game in user_games if game.result == '1/2-1/2']
    finished = [game for game in user_games if game.is_finished]
    unfinished = [game for game in user_games if not game.is_finished]
    db_sess.close()
    return render_template('profile.html', user=user, title=f'Профиль {user.nick}',
                           wins=wins, looses=looses, draws=draws, all=finished, unfinished=unfinished)


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
            db_sess.close()
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
        return render_template('login.html', title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        nick = request.form['nick'].lower()
        users = db_sess.query(User).filter(User.nick.like(f'%{nick}%')).all()
        db_sess.close()
        return render_template('search.html', users=users, title='Поиск')
    return render_template('search.html', title='Поиск', users=[])


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    db_sess.close()
    return user


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/register')


def create_new_game(p1, p2, game_type):
    db_sess = db_session.create_session()
    game = Game()
    game.white_player, game.black_player = sample((p1, p2), 2)
    game.type = game_type
    game.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    game.moves = ''
    db_sess.add(game)
    db_sess.commit()
    game.id = game.id
    db_sess.close()
    return game


def update_game(board, game):
    game.is_finished = 1
    game.result = board.result()
    wr, br = None, None
    if game.type == 'fast':
        db_sess = db_session.create_session()
        white = db_sess.get(User, game.white_player)
        black = db_sess.get(User, game.black_player)
        res = float(game.result.split('-')[0])
        wr = rating_calculation(white.rating, black.rating, res)
        br = rating_calculation(black.rating, white.rating, 1 - res)
        white.rating, black.rating = wr, br
        db_sess.commit()
        db_sess.close()
    if board.is_checkmate():
        game.reason = 'checkmate'
    elif board.is_stalemate():
        game.reason = 'stalemate'
    elif board.is_en_passant():
        game.reason = 'passant'
    return game.result, game.reason, wr, br


def get_board_game(game):
    board = Board()
    moves = game.moves.split()
    for move in moves:
        board.push(Move.from_uci(move))
    return board


if __name__ == '__main__':
    main()
