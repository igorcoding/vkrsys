require(['common'], function() {
    require(['jquery', 'PlayerApp/Player', 'UserCard'],
        function($, Player, UserCard) {
            $(document).ready(function($) {

                var loadContent = function() {
                    contentLoader.loadInitialRecommendations(window.TARGET_USERNAME, true, function(d) {
                        window.player = new Player("#main_player", "#main_playlist", ".user-cards", contentLoader);
                        console.log(player);
                    });
                };
                loadContent();
            });
        }
    );
});
