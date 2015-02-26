define(['jquery', 'jquery_ui', 'jquery_sizes', 'jquery_plugins', 'ContentLoader', 'Player'],
    function($, jquery_ui, jquery_sizes, jquery_plugins, ContentLoader, Player) {
        $(document).ready(function($) {
            var $window = $(window);
            window.onResizeFunctions = [];

            $window.resize(function() {
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

            window.contentLoader = new ContentLoader();
            contentLoader.fetchUserpic();
            contentLoader.loadInitialRecommendations(function(addedCount) {
                window.player = new Player("#main_player", "#main_playlist");
                console.log(player);

                $window.scroll(function() {
                    if($(window).scrollTop() == $(document).height() - $(window).height()) {
                        setTimeout(function() {
                            contentLoader.loadNextRecommendations();
                        }, 1000);
                    }
                });

            });



        });
    }
);