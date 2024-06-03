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

socket.on('friendly_game_url', function(data){$('#game-link').show().text(data)})