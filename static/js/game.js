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
  pieceTheme: '../static/img/chesspieces/' + pieces + '/{piece}.png',
  showErrors: console,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd,
  onDragStart: onDragStart,
  onMouseoutSquare: onMouseoutSquare,
  onMouseoverSquare: onMouseoverSquare,
}

function onDragStart (source, piece, position, orientation) {
  if (game.isGameOver()) return false

  if ((game.turn() === 'w' && ((piece.search(/^b/) !== -1) || !(role.includes('w')))) ||
      (game.turn() === 'b' && ((piece.search(/^w/) !== -1) || !(role.includes('b'))))) {
    return false
  }

  var moves = game.moves({
    square: source,
    verbose: true
  })

  for (var i = 0; i < moves.length; i++) {
    greySquare(moves[i].to)
  }

}

function onSnapEnd () {
  board.position(game.fen());
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
    if ((game.turn() === 'w' &&  !role.includes('w')) ||
        (game.turn() === 'b' && !role.includes('b'))) {
        return
    }
    var moves = game.moves({
        square: square,
        verbose: true
    })
    if (moves.length === 0) return

    greySquare(square)
}

function onMouseoutSquare (square, piece) {
  setColor(board_color)
}

function moveIn(moves, target) {
    for (var index = 0; index < moves.length; index++) {
        if (target === moves[index].to) return true;
    }
    return false;
}

socket.on('move', function(move) {
    game.move({from: move.from, to: move.to, promotion: 'q'})
    board.position(game.fen())
});

socket.on('game_over', function(data) {
    $('.end').text(data[0] + ' • ' + data[1])
    $('.analysis-link').text('Анализировать партию')
})

socket.on('reload', function() {
    location.reload();
});
