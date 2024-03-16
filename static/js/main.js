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
})