from chess import Board, square_name, square_file, square_rank, Piece, Move, parse_square


pieces = {Piece.from_symbol('r'): '♜',
          Piece.from_symbol('n'): '♞',
          Piece.from_symbol('b'): '♝',
          Piece.from_symbol('q'): '♛',
          Piece.from_symbol('k'): '♚',
          Piece.from_symbol('p'): '♟',
          Piece.from_symbol('R'): '♖',
          Piece.from_symbol('N'): '♘',
          Piece.from_symbol('B'): '♗',
          Piece.from_symbol('Q'): '♕',
          Piece.from_symbol('K'): '♔',
          Piece.from_symbol('P'): '♙',
          None: ''}


class HTMLBoard(Board):
    current = None

    def add_cell(self, cell):
        if self.current is None:
            if self.color_at(parse_square(cell)) == self.turn:
                self.current = cell
        elif cell == self.current:
            self.current = None
        else:
            move = Move.from_uci(self.current + cell)
            if not self.is_legal(move):
                self.current = None
                if self.color_at(parse_square(cell)) == self.turn:
                    self.current = cell
            else:
                self.push(move)
                self.current = None

    def get_board(self):
        lst = []
        for i in range(64):
            dct = {
                'name': square_name(i),
                'piece': pieces[self.piece_at(i)],
                'color': 'light' if (square_file(i) + square_rank(i)) % 2 else 'dark'
            }
            if self.current is not None:
                if dct['name'] == self.current:
                    dct['color'] = 'red'
                elif self.is_legal(Move.from_uci(self.current + dct['name'])):
                    dct['color'] = 'red'
            lst.append(dct)
        return lst
