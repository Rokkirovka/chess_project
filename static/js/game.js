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

function setColor(color){
    if (color == 'blue'){
        $('.white-1e1d7').css("background-color", "#e9eef2");
        $('.black-3c85d').css("background-color", "#8ca2ad");
    }
    else if (color == 'brown'){
        $('.white-1e1d7').css("background-color", "#f0d9b5");
        $('.black-3c85d').css("background-color", "#b58863");
    }
    else if (color == 'green'){
        $('.white-1e1d7').css("background-color", "#ffffdd");
        $('.black-3c85d').css("background-color", "#86a666");
    }
    else if (color == 'pink'){
        $('.white-1e1d7').css("background-color", "#ecedba");
        $('.black-3c85d').css("background-color", "#f07373");
    }
}

function onDragStart (source, piece, position, orientation) {
  if (game.isGameOver()) return false

  if ((game.turn() === 'w' && ((piece.search(/^b/) !== -1) || !(role.includes('w')))) ||
      (game.turn() === 'b' && ((piece.search(/^w/) !== -1) || !(role.includes('b'))))) {
    return false
  }
}

function onSnapEnd () {
  board.position(game.fen());
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

    if ((game.turn() === 'w' &&  !role.includes('w')) ||
      (game.turn() === 'b' && !role.includes('b'))) {
    return
    }
    if (moves.length === 0) return

  greySquare(square)

  for (var i = 0; i < moves.length; i++) {
    greySquare(moves[i].to)
  }
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
