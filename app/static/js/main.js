define(['jquery', 'jquery_ui', 'jquery_sizes', 'jquery_plugins', 'toastr', 'ContentLoader', 'Player'],
    function($, jquery_ui, jquery_sizes, jquery_plugins, toastr, ContentLoader, Player) {
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
            //contentLoader.loadInitialRecommendations(function(addedCount) {
                window.player = new Player("#main_player", "#main_playlist");
            //    console.log(player);
            //
            //    $window.scroll(function() {
            //        if(Math.ceil($(window).scrollTop()) >= $(document).height() - $(window).height()) {
            //
            //            setTimeout(function() {
            //                contentLoader.loadNextRecommendations();
            //            }, 1000);
            //        }
            //    });
            //
            //});



        });
    }
);