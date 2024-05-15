$(document).ready(function(){
    game = new Chess();
    board = Chessboard('chessboard', config);
    for (move of moves){
        game.move({from: move[0], to: move[1], promotion: 'q'})
    }
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

function move_click(id){
    board.position(game.history({verbose: true})[id].after)
    $.ajax({type: 'get', contentType: 'application/json', data: {fen: game.history({verbose: true})[id].after},
    success: function(data){$('.rate').text(data)}})
}