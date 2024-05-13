$(document).ready(function(){
    game = new Chess(fen);
    board = Chessboard('chessboard', config);
})


function onDrop(source, target){
    removeGreySquares()

    if (moveIn(game.moves({square: source, verbose: true}), target)){
        $.ajax({type: 'get', contentType: 'application/json', data: {from: source, to: target, id: id}})
    }
    else {
        return 'snapback'
    }
}