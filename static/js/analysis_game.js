$(document).ready(function(){
    game = new Chess();
    game_for_moves = new Chess();
    board = Chessboard('chessboard', config);
    for (move of moves){
        game_for_moves.move({from: move[0], to: move[1], promotion: 'q'})
        game.move({from: move[0], to: move[1], promotion: 'q'})
    }
    setColor(board_color);
    $.ajax({type: 'get', contentType: 'application/json', data: {fen: game.fen(), depth: 15},
    success: function(data){
        $('.rate').text(data.score)
        $('.depth').text(data.depth)
        depth = data.depth
        if (depth != 30) {
            $('.plus').show()
        }
    }
    })
})


function onDrop(source, target){}