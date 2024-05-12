const socket = io();
let board, game, orientation;
var whiteSquareGrey = '#a9a9a9';
var blackSquareGrey = '#696969';

if (role === 'b') {orientation = 'black'}
else {orientation = 'white'}

let config = {
  position: fen,
  orientation: orientation,
  showNotation: true,
  draggable: true,
  dropOffBoard: 'snapback',
  snapbackSpeed: 200,
  snapSpeed: 50,
  pieceTheme: '../static/img/chesspieces/wikipedia/{piece}.png',
  showErrors: 'console',
  onDrop: onDrop,
  onSnapEnd: onSnapEnd,
  onDragStart: onDragStart,
  onMouseoutSquare: onMouseoutSquare,
  onMouseoverSquare: onMouseoverSquare,
}

$(document).ready(function(){
    game = new Chess(fen);
    board = Chessboard('chessboard', config);
})

function onDragStart (source, piece, position, orientation) {
  if (game.isGameOver()) return false

  if ((game.turn() === 'w' && ((piece.search(/^b/) !== -1) || role !== 'w')) ||
      (game.turn() === 'b' && ((piece.search(/^w/) !== -1) || role !== 'b'))) {
    return false
  }
}

function onDrop(source, target){
    removeGreySquares()

    if (moveIn(game.moves({square: source, verbose: true}), target)){
        socket.emit('move', {from: source, to: target, id: id})
    }
    else {
        return 'snapback'
    }
}

function onSnapEnd () {
  board.position(game.fen());
}

socket.on('move', function(move) {
    board.move(move.from + '-' + move.to);
    game.move({from: move.from, to: move.to, promotion: 'q'})
});

socket.on('reload', function() {
    location.reload();
});

function removeGreySquares () {
  $('#chessboard .square-55d63').css('background', '')
}

function greySquare (square) {
  var $square = $('#chessboard .square-' + square)

  var background = whiteSquareGrey
  if ($square.hasClass('black-3c85d')) {
    background = blackSquareGrey
  }

  $square.css('background', background)
}

function onMouseoverSquare (square, piece) {
  var moves = game.moves({
    square: square,
    verbose: true
  })

    if ((game.turn() === 'w' &&  role !== 'w') ||
      (game.turn() === 'b' && role !== 'b')) {
    return
    }
    if (moves.length === 0) return

  greySquare(square)

  for (var i = 0; i < moves.length; i++) {
    greySquare(moves[i].to)
  }
}

function onMouseoutSquare (square, piece) {
  removeGreySquares()
}

function moveIn(moves, target) {
    for (var index = 0; index < moves.length; index++) {
        if (target === moves[index].to) return true;
    }
    return false;
}
