define(['jquery', 'jquery_ui', 'jquery_sizes', 'jquery_plugins', 'toastr', 'ContentLoader', 'PlayerControl'],
    function($, jquery_ui, jquery_sizes, jquery_plugins, toastr, ContentLoader, PlayerControl) {
        $(document).ready(function($) {
            toastr.options = toastr.options = {
              "closeButton": false,
              "debug": false,
              "newestOnTop": true,
              "progressBar": false,
              "positionClass": "toast-top-right",
              "preventDuplicates": true,
              "onclick": null,
              "showDuration": "300",
              "hideDuration": "1000",
              "timeOut": "5000",
              "extendedTimeOut": "1000",
              "showEasing": "swing",
              "hideEasing": "linear",
              "showMethod": "fadeIn",
              "hideMethod": "fadeOut"
            };

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

            window.durationToTime = function(duration) {
                return duration;
            };

            window.contentLoader = new ContentLoader();
            contentLoader.fetchUserpic();
            contentLoader.loadInitialRecommendations(function(addedCount) {
                window.player = new PlayerControl("#main_player");
                console.log(player);

                var loading = false;
                player.playlist.addOnScrollListener(function($el) {
                    if(!loading && Math.ceil($el.scrollTop()) >= $el.prop('scrollHeight') - $el.height() - 700) {
                        console.log("loading");
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



        });
    }
);