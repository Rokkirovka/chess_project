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

colors = {'light': '#e9eef2',
          'dark': ' #8ca2ad',
          'light-red': '#507b65',
          'dark-red': '#789b81',
          'light-green': '#c3d888',
          'light-purple': '#876c99'}


class HTMLBoard(Board):
    current = None

    def add_cell(self, cell):
        if self.current is None:
            if self.color_at(parse_square(cell)) == self.turn:
                self.current = cell
        elif cell == self.current:
            self.current = None
        else:
            if (pieces[self.piece_at(parse_square(self.current))] == '♙' and self.current[1] == '7' and cell[1] == '8'
                    or pieces[self.piece_at(parse_square(self.current))] == '♟' and self.current[1] == '2' and cell[
                        1] == '1'):
                move = Move.from_uci(self.current + cell + 'q')
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
                'color': colors['light'] if (square_file(i) + square_rank(i)) % 2 else colors['dark'],
                'add_color': colors['light'] if (square_file(i) + square_rank(i)) % 2 else colors['dark']
            }
            if self.move_stack:
                if self.move_stack[-1].uci()[2:] == square_name(i) or self.move_stack[-1].uci()[:2] == square_name(i):
                    dct['color'] = colors['light-green']
                    dct['add_color'] = colors['light-green']
            if self.piece_at(i) == Piece.from_symbol('K') and self.turn and self.is_check():
                dct['color'] = colors['light-purple']
                dct['add_color'] = colors['light-purple']
            if self.piece_at(i) == Piece.from_symbol('k') and not self.turn and self.is_check():
                dct['color'] = colors['light-purple']
                dct['add_color'] = colors['light-purple']
            if self.current is not None:
                if dct['name'] == self.current:
                    dct['add_color'] = colors['dark-red']
                elif self.is_legal(Move.from_uci(self.current + dct['name'])) or self.is_legal(
                        Move.from_uci(self.current + square_name(i) + 'q')):
                    dct['add_color'] = colors['light-red']
            lst.append(dct)
        return lst

    def get_board_for_ajax(self):
        dct = {'cells': {}, 'turn': self.turn}
        for i in range(64):
            if (square_file(i) + square_rank(i)) % 2:
                color = colors['light']
            else:
                color = colors['dark']
            if self.move_stack:
                if self.move_stack[-1].uci()[2:] == square_name(i) or self.move_stack[-1].uci()[:2] == square_name(i):
                    color = colors['light-green']
            if self.piece_at(i) == Piece.from_symbol('K') and self.turn and self.is_check():
                color = colors['light-purple']
            if self.piece_at(i) == Piece.from_symbol('k') and not self.turn and self.is_check():
                color = colors['light-purple']
            if square_name(i) == self.current:
                color = colors['dark-red']
            elif self.current and (self.is_legal(Move.from_uci(self.current + square_name(i))) or self.is_legal(
                    Move.from_uci(self.current + square_name(i) + 'q'))):
                color = colors['light-red']
            dct['cells'][square_name(i)] = {'piece': pieces[self.piece_at(i)], 'color': color}
        return dct

    def get_board_for_socket(self):
        dct = {'cells': {}, 'turn': self.turn}
        for i in range(64):
            if (square_file(i) + square_rank(i)) % 2:
                color = colors['light']
            else:
                color = colors['dark']
            if self.move_stack:
                if self.move_stack[-1].uci()[2:] == square_name(i) or self.move_stack[-1].uci()[:2] == square_name(i):
                    color = colors['light-green']
            dct['cells'][square_name(i)] = {'piece': pieces[self.piece_at(i)], 'color': color}
        return dct
