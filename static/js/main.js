const socket = io();

window.cell = null;

socket.on('update_board', (response) => {
    if (response.end_game == true){
        $('.end').text(response.result + ' • ' + response.reason)
    }
    print_board(response)
});

socket.on('reload', function() {
    location.reload();
});

function cell_start_drag(id) {
    window.cell = id
    $.ajax({url: '', type: 'get', contentType: 'application/json',
        data: {type: 'cell', cell: window.cell}, success: print_board
    })
}

function cell_drag_over(event) {
    event.preventDefault();
}


function cell_drop(id) {
    let move = window.cell + id;
    $.ajax({
        url: '', type: 'get', contentType: 'application/json',
        data: {type: 'move', move: move}
    })
}


function cell_click(id) {
    if (window.cell == null){
        $.ajax({
            url: '', type: 'get', contentType: 'application/json',
            data: {type: 'cell', cell: id}, success: print_board
        })
    }
    else {
        let move = window.cell + id
        window.cell = null
        $.ajax({
            url: '', type: 'get', contentType: 'application/json',
            data: {type: 'move', move: move}, success: print_board
        })
    }
}

function move_click(id) {
    $.ajax({
        url: '', type: 'get', contentType: 'application/json',
        data: {move_number: id},
        success: function(response){
            document.getElementsByClassName('progress-bar-completed')[0].style.height = response[response.length - 1] + "%";
            for (var cell in response.slice(0, -2)){
                $('.chess-board [id=' + response[cell].name + '] .cell-piece').text(response[cell].piece);
                $('.chess-board [id=' + response[cell].name + ']').css('background-color', response[cell].color);
            };
        }
    })
}


function print_board(response){
    for (var cell in response.slice(0, -1)){
        $('.chess-board [id=' + response[cell].name + '] .cell-piece').text(response[cell].piece);
        $('.chess-board [id=' + response[cell].name + ']').css('background-color', response[cell].color);
    };
    window.cell = response[response.length - 1].current;
}