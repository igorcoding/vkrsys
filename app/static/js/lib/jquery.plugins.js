$.fn.totalWidth = function() {
    var margin = this.margin();
    return this.width() + margin.left + margin.right;
};

$.fn.textWidth = function() {
    var html_org = $(this).html();
    var html_calc = '<span>' + html_org + '</span>';
    $(this).html(html_calc);
    var width = $(this).find('span:first').width();
    $(this).html(html_org);
    return width;
};

$.fn.tilted = function(click_cb) {
    var obj_tilted = false;
    var $obj = $(this);
    click_cb = click_cb || function() {};
    $obj
        .on('mousedown', function(e) {
            e.preventDefault();
            $obj.addClass('tilted');
            obj_tilted = true;
            $(window).on('mouseup', function() {
                if (obj_tilted) {
                    $obj.removeClass('tilted');
                    obj_tilted = false;
                }
                $(this).off('mouseup');
            });
        })
        .on('mouseup', function() {
            $obj.removeClass('tilted');
            obj_tilted = false;
            $(window).off('mouseup');
        })
        .on('click', click_cb);
};