$(document).ready(function(){
    game = new Chess(fen);
    board = Chessboard('chessboard', config);
})


function onDrop(source, target){
    removeGreySquares()

    if (moveIn(game.moves({square: source, verbose: true}), target)){
        game.move({from: source, to: target, promotion: 'q'})
        $.ajax({type: 'get', contentType: 'application/json', data: {fen: game.fen()},
        success: function(data){$('.rate').text(data)}})
    }
    else {
        return 'snapback'
    }
}