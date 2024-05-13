$(document).ready(function(){
    game = new Chess(fen);
    board = Chessboard('chessboard', config);
    if (role === 'b'){
        $.ajax({type: 'get', contentType: 'application/json', data: {fen: game.fen(), level: level},
        success: function(data){game.move({from: data.from, to: data.to, promotion: 'q'}); board.move(data.from + '-' + data.to)}})
    }
})


function onDrop(source, target){
    removeGreySquares()

    if (moveIn(game.moves({square: source, verbose: true}), target)){
        game.move({from: source, to: target, promotion: 'q'})
        if (!game.isGameOver()){
            $.ajax({type: 'get', contentType: 'application/json', data: {fen: game.fen(), level: level},
            success: function(data){game.move({from: data.from, to: data.to, promotion: 'q'}); board.move(data.from + '-' + data.to)}})
        }
    }
    else {
        return 'snapback'
    }
}