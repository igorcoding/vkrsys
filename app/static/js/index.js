require.config({
    urlArgs: "_=",// + (new Date()).getTime(),
    baseUrl: "/static/js",
    paths: {
        jquery: "lib/jquery.min",
        jquery_ui: "lib/jquery-ui.min",
        jquery_sizes: "lib/jquery.sizes.min",
        jquery_totalWidth: "lib/jquery.totalWidth",
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

        'jquery_totalWidth': {
            deps: ['jquery'],
            exports: '$'
        }
    }
});

requirejs(['main']);
