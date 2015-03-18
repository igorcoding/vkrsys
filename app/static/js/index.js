require.config({
    urlArgs: "_=",// + (new Date()).getTime(),
    baseUrl: "/static/js",
    paths: {
        jquery: "lib/jquery.min",
        jquery_ui: "lib/jquery-ui.min",
        jquery_sizes: "lib/jquery.sizes.min",
        jquery_plugins: "lib/jquery.plugins",
        lodash: "lib/lodash.min"
    },
    shim: {
        'lodash': {
            exports: '_'
        },
        'jquery': {
            exports: '$'
        },
        'jquery_ui': {
            deps: ['jquery'],
            exports: '$'
        },
        'jquery_sizes': {
            deps: ['jquery'],
            exports: '$'
        },

        "jquery_plugins": {
            deps: ['jquery'],
            exports: '$'
        }
    }
});

requirejs(['main']);
