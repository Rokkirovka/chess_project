$(document).ready(function(){
    $('.cell').click(function(){
        $.ajax({
            url: '',
            type: 'get',
            contentType: 'application/json',
            data: {
                cell: $(this).attr('name')
            },
            success: function(response){
                for (var cell in response.cells){
                    $('[name=' + cell + ']').text(response.cells[cell]['piece']);
                    $('[name=' + cell + ']').removeClass().addClass(response.cells[cell]['color']);
                }
            }
        })
    })
})