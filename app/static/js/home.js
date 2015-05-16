require(['common'], function() {
    require(['jquery', 'PlayerApp/PlayerControl'],
        function($, PlayerControl) {
            $(document).ready(function($) {

                var loadContent = function() {
                    contentLoader.loadInitialRecommendations(true, function(d) {
                        window.player = new PlayerControl("#main_player", contentLoader, {
                            playpause: 'p',
                            prev: 'b',
                            next: 'n',
                            like: 'l',
                            dislike: 'd',
                            refresh: 'r'
                        });
                        console.log(player);

                        var loading = false;
                        player.playlist.addOnScrollListener(function($el) {
                            if(!loading && Math.ceil($el.scrollTop()) >= $el.prop('scrollHeight') - $el.height() - 700) {
                                //console.log("loading");
                                loading = true;
                                setTimeout(function() {
                                    contentLoader.loadNextRecommendations(function(d) {
                                        loading = false;
                                        window.player.playlist.addContent(d);
                                    });
                                }, 1000);
                            }
                        }.bind(this));
                    });
                };
                loadContent();
            });
        }
    );
});
