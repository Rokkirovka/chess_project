import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Game(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'games'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    white_player = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    black_player = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    cell = sqlalchemy.Column(sqlalchemy.String)
    moves = sqlalchemy.Column(sqlalchemy.String)
    position = sqlalchemy.Column(sqlalchemy.String)
    turn = sqlalchemy.Column(sqlalchemy.Boolean)
    result = sqlalchemy.Column(sqlalchemy.String)
    reason = sqlalchemy.Column(sqlalchemy.String)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean)
