require(['common'], function() {
    require(['jquery'],
        function($) {
            $(document).ready(function($) {
                contentLoader.fetchMainUserpic();
            });
        }
    );
});