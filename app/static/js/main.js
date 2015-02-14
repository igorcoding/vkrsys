(function ($) {
    $.fn.totalWidth = function() {
        var margin = this.margin();
        return this.width() + margin.left + margin.right;
    };
})(jQuery);

jQuery(document).ready(function($) {
    window.onResizeFunctions = [];

    $(window).resize(function() {
        for (var i = 0; i < window.onResizeFunctions.length; ++i) {
            onResizeFunctions[i](window);
        }
    });

    window.registerOnResize = function(func, ctx) {
        ctx = ctx || window;
        onResizeFunctions.push(func.bind(ctx));
    };

    window.rawC = function(c) {
        return c.substring(1);
    };

    window.player = new Player("#main_player", "#main_playlist");
    console.log(player);


});