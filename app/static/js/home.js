require(['common'], function() {
    require(['jquery', 'PlayerApp/Player', 'UserCard'],
        function($, Player, UserCard) {
            $(document).ready(function($) {

                var loadContent = function() {
                    contentLoader.loadInitialRecommendations(window.TARGET_USERNAME, true, function(d) {
                        window.player = new Player("#main_player", "#main_playlist", ".user-cards", contentLoader);
                        console.log(player);

                        var loading = false;
                        player.playlist.addOnScrollListener(function($el) {
                            if(!loading && Math.ceil($el.scrollTop()) >= $el.prop('scrollHeight') - $el.height() - 700) {
                                //console.log("loading");
                                loading = true;
                                setTimeout(function() {
                                    contentLoader.loadNextRecommendations(window.TARGET_USERNAME, function(d) {
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
