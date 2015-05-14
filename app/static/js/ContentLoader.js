define(['jquery'],
    function($) {
        function ContentLoader() {
            this.$obj = $(document);
            this.DOM = {};
            this.bindToDOM();
            this.limit = 50;
            this.offset = 0;
        }

        ContentLoader.prototype = {
            C: {
                UserAvatar: '.main-header__toolbar__user__avatar',
                MainContentInner: '.main-content',
                Loader: '.loader'
            },

            bindToDOM: function () {
                for (var key in this.C) {
                    if (this.C.hasOwnProperty(key)) {
                        if (key !== 'IGNORED') {
                            this.DOM[key] = this.$obj.find(this.C[key]);
                        }
                    }
                }
            },

            fetchUserpic: function () {
                var self = this;
                $.ajax('/api/userpic', {
                    method: 'GET'
                })
                    .done(function (d) {
                        if (d.status == 401) {
                            window.location.href = d.redirect_url;
                            return;
                        }
                        if (d.status === 200) {
                            console.log('[userpic] loaded');
                            self.DOM.UserAvatar.css('background-image', 'url(' + d.url + ')')
                        } else if (d.status !== 501) {
                            setTimeout(function () {
                                console.log('[userpic] Retrying to fetch userpic');
                                self.fetchUserpic();
                            }, 5000);
                        }
                    })
                    .fail(function (d) {
                        console.warn('[userpic] disaster: ', d);
                    });
            },

            loadInitialRecommendations: function (withContent, cb) {
                var self = this;
                cb = cb || function () {};

                this.offset = 0;
                this.loadRecommendations(this.limit, this.offset, true, withContent, function (d) {
                    if (withContent) {
                        self.DOM.Loader.remove();
                        self.bindToDOM();
                        self.DOM.MainContentInner.prepend(d.result);
                    }
                    cb(d);
                }, self.loadInitialRecommendations.bind(self, withContent, cb));
            },

            loadNextRecommendations: function (cb) {
                var self = this;
                cb = cb || function () {};

                this.loadRecommendations(this.limit, this.offset, false, false, function (d) {
                    //if (d.count == 0) {
                    //    self.DOM.Loader.hide();
                    //}
                    cb(d);
                }, self.loadNextRecommendations.bind(self, cb));
            },

            loadRecommendations: function (limit, offset, initial, withContent, cb, funcToRetry) {
                var self = this;
                cb = cb || function () {};

                var retrial = function (timeout) {
                    setTimeout(function () {
                        console.log('[recommend] Retrying to fetch recommendations');
                        funcToRetry();
                    }, timeout);
                };

                $.ajax('/api/recommend', {
                    method: 'GET',
                    data: {
                        limit: limit,
                        offset: offset,
                        initial: initial ? 1 : 0,
                        with_content: withContent ? 1 : 0
                    }
                })
                    .done(function (d) {
                        if (d.status == 401) {
                            window.location.href = d.redirect_url;
                            return;
                        }
                        if (d.status == 200) {
                            self.offset += d.count;
                            cb(d);
                        } else {
                            retrial(500);
                        }
                    })
                    .fail(function (d) {
                        console.warn('[recommend] disaster: ', d);
                        retrial(2000);
                    });
            }
        };

        return ContentLoader;
    }
);
