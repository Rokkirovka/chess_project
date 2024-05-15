import datetime
from random import choice

from data.engine import engine_move, engine_analysis
from chess import Move, parse_square, Board, square_name
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_socketio import SocketIO, emit
from flask_restful import Api
from data import chess_resources

from data import db_session
from data.games import Game, EngineGame
from data.rating_calculator import rating_calculation
from data.users import User
from forms.user import RegisterForm, GameForm, LoginForm, GameEngineForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
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


@app.route('/create_game', methods=['GET', 'POST'])
@login_required
def new_game():
    db_sess = db_session.create_session()
    user = db_sess.get(User, current_user.id)
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
    user = db_sess.get(User, current_user.id)
    game = db_sess.query(Game).filter(
        ((Game.black_player == int(user.id)) | (Game.white_player == int(user.id))) & (Game.type == 'fast')).filter(
        (Game.black_player == None) | (Game.white_player == None)).first()
    if not game:
        games = db_sess.query(Game).filter(
            ((Game.black_player == None) | (Game.white_player == None)) & (Game.type == 'fast')).all()
        if games:
            game = choice(games)
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


@app.route('/engine_game', methods=['GET', 'POST'])
@login_required
def new_engine_game():
    if request.is_json:
        data = request.args
        move = engine_move(data['fen'], data['level'])
        return jsonify({'from': square_name(move.from_square), 'to': square_name(move.to_square)})
    form = GameEngineForm()
    if form.validate_on_submit():
        if form.color.data == '3':
            color = choice(['w', 'b'])
        else:
            color = 'w' if form.color.data == '1' else 'b'
        board = Board()
        if color == 'b':
            board.push(engine_move(board.fen(), form.level.data))
        return render_template('engine_game.html', level=form.level.data, role=color)
    return render_template('create_engine_game.html', form=form)


@app.route('/game/<int:game_id>')
def play_game(game_id):
    db_sess = db_session.create_session()
    game = db_sess.get(Game, game_id)
    if request.is_json:
        data = request.args
        board = Board(game.fen)
        board.push(Move.from_uci(data['from'] + data['to']))
        game.fen = board.fen()
        db_sess.commit()
        socketio.emit('move', data)
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
    board = get_board_game(game)
    white_player = db_sess.get(User, game.white_player)
    black_player = db_sess.get(User, game.black_player)
    db_sess.close()
    if request.is_json:
        data = request.args
        score = engine_analysis(data['fen'])
        return jsonify(score)
    moves = [[square_name(move.from_square), square_name(move.to_square)] for move in board.move_stack]
    score = engine_analysis(board.fen())
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
    board = Board()
    if request.is_json:
        data = request.args
        score = engine_analysis(data['fen'])
        return jsonify(score)
    score = engine_analysis(board.fen())
    return render_template('analysis_position.html', score=score, title='Анализ')


@app.route('/profile/<int:user_id>')
def profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    all_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) |
                                            (Game.white_player == int(user.id))) & (Game.is_finished == 1)).all()
    all_games = {x.id: [x, get_board_game(x).get_board_for_json()] for x in all_games}
    win_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) & (Game.result == 'Black win')) |
                                           ((Game.white_player == int(user.id)) & (Game.result == 'White win'))).all()
    win_games = {x.id: [x, get_board_game(x).get_board_for_json()] for x in win_games}
    draw_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) |
                                             (Game.white_player == int(user.id))) & (Game.result == 'Draw')).all()
    draw_games = {x.id: [x, get_board_game(x).get_board_for_json()] for x in draw_games}
    loose_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) & (Game.result == 'White win')) |
                                             ((Game.white_player == int(user.id)) & (Game.result == 'Black win'))).all()
    loose_games = {x.id: [x, get_board_game(x).get_board_for_json()] for x in loose_games}
    unfinished_games = db_sess.query(Game).filter(((Game.black_player == int(user.id)) |
                                                   (Game.white_player == int(user.id))) & (Game.is_finished == 0)).all()
    unfinished_games = {x.id: [x, get_board_game(x).get_board_for_json()] for x in unfinished_games}
    db_sess.close()
    return render_template('profile.html', user=user, title=f'Профиль {user.nick}',
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
        return render_template('search.html', users=users, title='Поиск',)
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


def check_position(fen, white_player=None, black_player=None):
    wr, br = None, None
    is_finished = 1
    board = Board(fen)
    if board.is_checkmate():
        reason = 'Checkmate'
        if board.turn:
            result = 'Black win'
            if white_player is not None and black_player is not None:
                wr = rating_calculation(white_player.rating, black_player.rating, 0)
                br = rating_calculation(black_player.rating, white_player.rating, 1)
        else:
            result = 'White win'
            if white_player is not None and black_player is not None:
                wr = rating_calculation(white_player.rating, black_player.rating, 1)
                br = rating_calculation(black_player.rating, white_player.rating, 0)
    elif board.is_stalemate():
        result = 'Draw'
        reason = 'Stalemate'
        wr = rating_calculation(white_player.rating, black_player.rating, 0.5)
        br = rating_calculation(black_player.rating, white_player.rating, 0.5)
    else:
        reason, is_finished, result = None, 0, None
    return result, reason, is_finished, wr, br


def update_game(game, result, reason, is_finished, wr, br, white_player, black_player):
    if is_finished:
        game.is_finished = 1
        game.result = result
        game.reason = reason
    if wr is not None and br is not None:
        white_player.rating = wr
        black_player.rating = br
    return


def get_board_game(game):
    board = Board()
    moves = game.moves.split()
    for move in moves:
        board.push(Move.from_uci(move))
    return board


if __name__ == '__main__':
    main()
