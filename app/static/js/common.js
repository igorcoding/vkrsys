define(['jquery', 'jquery_sizes', 'jquery_plugins', 'toastr', 'PlayerApp/ContentLoader'],
    function ($, _1, _2, toastr, ContentLoader) {
        $(document).ready(function ($) {
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

            $window.resize(function () {
                for (var i = 0; i < window.onResizeFunctions.length; ++i) {
                    onResizeFunctions[i](window);
                }
            });

            window.registerOnResize = function (func, ctx) {
                ctx = ctx || window;
                onResizeFunctions.push(func.bind(ctx));
            };

            window.rawC = function (c) {
                return c.substring(1);
            };

            window.durationToTime = function (duration) {
                return duration;
            };

            var $userProfileButtton = $('#user_profile_button');
            $('#main_header_title').tilted();
            $userProfileButtton.tilted();
            $('#share_button').tilted(function (e) {
                e.preventDefault();
            });
            $('#logout_button').tilted();

            window.contentLoader = new ContentLoader();
            contentLoader.fetchMainUserpic();
        });
    }
);
