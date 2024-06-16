$(document).ready(function(){
    game = new Chess(fen);
    board = Chessboard('chessboard', config);
    socket.emit('join_game', {game_id: id});
    setColor(board_color);
})


function onDrop(source, target){
    setColor(board_color)

    if (moveIn(game.moves({square: source, verbose: true}), target)){
        $.ajax({type: 'get', contentType: 'application/json', data: {from: source, to: target, id: id}})
    }
    else {
        return 'snapback'
    }
}