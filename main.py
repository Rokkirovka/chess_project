from random import choice

from flask import Flask, render_template, request, redirect, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_socketio import SocketIO

from data import db_session
from data.rating_calculator import rating_calculation
from data.chess_to_html import HTMLBoard
from data.games import Game
from data.users import User
from forms.user import RegisterForm, GameForm, LoginForm

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
    form = GameForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        opponent = db_sess.query(User).filter(User.nick == form.opponent.data).first()
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
        game.position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
        game.turn = True
        game.is_finished = False
        db_sess.add(game)
        db_sess.commit()
        return redirect('/game/' + str(game.id))
    return render_template('create_game.html', form=form)


@app.route('/game/<game_id>')
def play_game(game_id):
    db_sess = db_session.create_session()
    game = db_sess.query(Game).filter(Game.id == game_id).first()
    white_player = db_sess.query(User).filter(User.id == game.white_player).first()
    black_player = db_sess.query(User).filter(User.id == game.black_player).first()
    board = HTMLBoard(game.position)
    board.current = game.cell
    board.turn = game.turn
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
            game.position = board.board_fen()
            game.turn = board.turn
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
                           result=game.result, reason=game.reason)


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
        if db_sess.query(User).filter((User.email == form.email.data) | (User.nick == form.nick.data)).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nick=form.nick.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        user.rating = 1500
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        login_user(user, remember=True)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
