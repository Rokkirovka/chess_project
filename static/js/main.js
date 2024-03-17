const socket = io();
$(document).ready(function(){
    $('.chess-board .cell-button').click(function(){
        $.ajax({
            url: '',
            type: 'get',
            contentType: 'application/json',
            data: {
                cell: $(this).attr('name')
            },
            success: function(response){
                for (var cell in response.cells){
                    $('.chess-board [name=' + cell + '] .cell-piece').text(response.cells[cell]['piece']);
                    $('.chess-board [name=' + cell + ']').css('background-color', response.cells[cell]['color']);
                }
            }
        })
    })
});
socket.on('update_board', (response) => {
    if (response.end_game == true){
        $('.end').text(response.result + ' • ' + response.reason)
    }
    for (var cell in response.cells){
        $('.chess-board [name=' + cell + '] .cell-piece').text(response.cells[cell]['piece']);
        $('.chess-board [name=' + cell + ']').css('background-color', response.cells[cell]['color']);
    }
});