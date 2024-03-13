from random import choice

from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, login_required, current_user

from data import db_session
from data.chess_to_html import HTMLBoard
from data.games import Game
from data.users import User
from forms.user import RegisterForm, GameForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init('db/chess.db')
    app.run()


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
        if form.color.data == 'случайно':
            color = choice(['белые', 'черные'])
        else:
            color = form.color.data
        if color == '1':
            game.white_player = current_user.id
            game.black_player = opponent.id
        else:
            game.black_player = current_user.id
            game.white_player = opponent.id
        game.position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/QNBQKBNR'
        game.turn = True
        game.is_finished = False
        db_sess.add(game)
        db_sess.commit()
        return redirect('/play_game/' + str(game.id))
    return render_template('create_game.html', form=form)


@app.route('/play_game/<game_id>', methods=['POST', 'GET'])
@login_required
def play_game(game_id):
    db_sess = db_session.create_session()
    game = db_sess.query(Game).filter(Game.id == game_id).first()
    board = HTMLBoard(game.position)
    board.current = game.cell
    board.turn = game.turn
    if request.method == 'POST':
        cell = list(request.form.keys())[0]
        board.add_cell(cell)
        game.cell = board.current
        game.position = board.board_fen()
        game.turn = board.turn
        db_sess.commit()
    lst = board.get_board()
    return render_template('game.html', board=lst, white=game.white_player,
                           black=game.black_player, turn=game.turn)


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
        login_user(user)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    main()
