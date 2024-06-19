validFen = true

$(document).ready(function(){
    let config = {
        position: 'start',
        sparePieces: true,
        showNotation: true,
        draggable: true,
        dropOffBoard: 'trash',
        snapbackSpeed: 200,
        snapSpeed: 50,
        pieceTheme: '../static/img/chesspieces/' + pieces + '/{piece}.png'
    }
    game = new Chess();
    board = Chessboard('chessboard', config);
    setColor(board_color);

    $('#white-turn').prop('checked', true);
    $('#white-turn').change(function() {
      if ($(this).is(':checked')) {
        $('#black-turn').prop('checked', false);
      }
      else {
        $('#white-turn').prop('checked', true);
      }
    });

    $('#black-turn').change(function() {
      if ($(this).is(':checked')) {
        $('#white-turn').prop('checked', false);
      }
      else {
        $('#black-turn').prop('checked', true);
      }
    });
})

function checkFen(){
    if ($('#white-turn').is(':checked')) {
        var move = 'w'
    }
    else {
        var move = 'b'
    }

    if ($('#black-rok-0-0').is(':checked')) {var k = 'k'}
    else{var k = ''}

    if ($('#black-rok-0-0-0').is(':checked')) {var q = 'q'}
    else{var q = ''}

    if ($('#white-rok-0-0').is(':checked')) {var K = 'K'}
    else{var K = ''}

    if ($('#white-rok-0-0-0').is(':checked')) {var Q = 'Q'}
    else{var Q = ''}
    if (k == '' && K == '' && q == '' && Q == ''){K = '-'}
    var fen = board.fen() + ' ' + move + ' ' + K + Q + k + q + ' - 0 1'

    data = validateFen(fen)
    $('#error').text(data.error)
    return {ok: data.ok, fen: fen}
}

function playBotFen(){
    data = checkFen()
    const chess = new Chess()
    chess.load(data.fen)
    if (data.ok == true){
        window.location.href = window.location.origin + '/engine_game' + '?fen=' + data.fen + '&color=' + chess.turn()
    }
}

function analysisFen(){
    data = checkFen()
    if (data.ok == true){
        window.location.href = window.location.origin + '/analysis' + '?fen=' + data.fen
    }
}