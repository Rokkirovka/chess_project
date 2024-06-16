const socket = io();

function showTabContent(contentId) {
    $(".tab-content").children().hide();
    $("#" + contentId).show();
}

function showDropdownContent(contentId){
    if ($("#" + contentId).is(':hidden')) {
        $('.dropdown-content').hide();
        $("#" + contentId).show();
        $("#" + contentId).css('display', 'flex');
    } else {
        $("#" + contentId).hide();
    }
}

function fastGame(){
    if ($('.dot-container').is(':hidden')){
        $('.home-item').hide()
        $('#fast-game').show().text('Подбор противника')
        socket.emit('append_fast_game')
        $('.dot-container').show();
    }
    else{
        $('.home-item').show()
        $('#fast-game').text('Быстрая игра')
        socket.emit('remove_fast_game')
        $('.dot-container').hide()
        $('#game-link').hide()
    }
}

function friendlyGame(){
    if ($('#game-link').is(':hidden')){
        $('.home-item').hide()
        $('#friendly-game').show().text('Отправьте ссылку другу')
        socket.emit('append_friendly_game')
    }
    else{
        $('.home-item').show()
        $('#friendly-game').text('Играть с другом')
        socket.emit('remove_friendly_game')
        $('#game-link').hide()
    }
}

function changePieces(name){
    socket.emit('change_piece', name)
    location.reload()
}

function changeBoard(name){
    socket.emit('change_board', name)
    location.reload()
}

function setColor(color){
    if (color == 'blue'){
        $('.white-1e1d7').css("background-color", "#e9eef2");
        $('.black-3c85d').css("background-color", "#8ca2ad");
    }
    else if (color == 'brown'){
        $('.white-1e1d7').css("background-color", "#f0d9b5");
        $('.black-3c85d').css("background-color", "#b58863");
    }
    else if (color == 'green'){
        $('.white-1e1d7').css("background-color", "#ffffdd");
        $('.black-3c85d').css("background-color", "#86a666");
    }
    else if (color == 'pink'){
        $('.white-1e1d7').css("background-color", "#ecedba");
        $('.black-3c85d').css("background-color", "#f07373");
    }
}

socket.on('friendly_game_url', function(data){$('#game-link').show().text(data)})

function upDepth(){
    depth += 3
    $('.rate').text('...')
    $('.depth').text(depth)
    $('.plus').hide()
    $.ajax({type: 'get', contentType: 'application/json', data: {fen: game.fen(), depth: depth},
        success: function(data){
            $('.rate').text(data.score)
            if (depth != 30) {
                $('.plus').show()
            }
        }
    })
}

function move_click(id){
    board.position(game_for_moves.history({verbose: true})[id].after)
    game = new Chess(game_for_moves.history({verbose: true})[id].after)
    $('.rate').text('...')
    $('.depth').text(depth)
    $('.plus').hide()
    $.ajax({type: 'get', contentType: 'application/json', data: {fen: game.fen(), depth: 15},
    success: function(data){
        $('.rate').text(data.score)
        $('.depth').text(data.depth)
        depth = data.depth
        if (depth != 30) {
            $('.plus').show()
        }
    }})
}