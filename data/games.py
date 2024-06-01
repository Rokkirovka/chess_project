import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Game(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'games'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    white_player = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    black_player = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    moves = sqlalchemy.Column(sqlalchemy.String)
    fen = sqlalchemy.Column(sqlalchemy.String)
    result = sqlalchemy.Column(sqlalchemy.String)
    reason = sqlalchemy.Column(sqlalchemy.String)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=0)
    type = sqlalchemy.Column(sqlalchemy.String)
