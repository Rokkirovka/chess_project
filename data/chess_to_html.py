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


class ImprovedBoard(Board):
    def make_move(self, move):
        current = None
        if move[:2] == move[2:]:
            current = None
        elif self.color_at(parse_square(move[2:])) == self.turn:
            current = move[2:]
        if move[:2] != move[2:]:
            push_move = Move.from_uci(move)
            if self.is_legal(push_move):
                self.push(push_move)
                current = None
        return current

    def get_board_for_json(self, selected=None):
        json_board = []
        for i in range(64):
            cell = {
                'name': square_name(i),
                'piece': pieces[self.piece_at(i)],
                'color': colors['light'] if (square_file(i) + square_rank(i)) % 2 else colors['dark']
            }
            if self.move_stack:
                if self.move_stack[-1].uci()[2:] == square_name(i) or self.move_stack[-1].uci()[:2] == square_name(i):
                    cell['color'] = colors['light-green']
            if self.piece_at(i) == Piece.from_symbol('K') and self.turn and self.is_check():
                cell['color'] = colors['light-purple']
            if self.piece_at(i) == Piece.from_symbol('k') and not self.turn and self.is_check():
                cell['color'] = colors['light-purple']
            if selected is not None:
                if selected == square_name(i):
                    cell['color'] = colors['dark-red']
                elif self.is_legal(Move.from_uci(selected + square_name(i))):
                    cell['color'] = colors['light-red']
            json_board.append(cell)
        json_board.append({'current': selected})
        return json_board
