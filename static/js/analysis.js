var move = 0;

$(document).ready(function(){
    table = document.getElementById("moves-table");
    game = new Chess(fen);
    $('.plus').hide();
    board = Chessboard('chessboard', config);
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


function onDrop(source, target){
    setColor(board_color)

    if (moveIn(game.moves({square: source, verbose: true}), target)){
        game.move({from: source, to: target, promotion: 'q'})
        depth = 15;
        $('.rate').text('...')
        $('.depth').text(depth)
        $.ajax({type: 'get', contentType: 'application/json', data: {fen: game.fen(), depth: 15},
        success: function(data){
            $('.rate').text(data.score)
            $('.depth').text(data.depth)
            depth = data.depth
            if (depth != 30) {
            $('.plus').show()
        }
        }})

        if (move % 2 == 0){
            row = table.insertRow();
            var cell = row.insertCell(0);
            cell.innerHTML = move + 1
            var cell = row.insertCell(1);
            cell.innerHTML = source + target
        }
        else {
            var cell = row.insertCell(2);
            cell.innerHTML = source + target
        }
        move += 1
    }
    else {
        return 'snapback'
    }
}