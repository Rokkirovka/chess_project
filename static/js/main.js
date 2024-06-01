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