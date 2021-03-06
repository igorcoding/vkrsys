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
                MainContentInner: '.main-container',
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

            fetchMainUserpic: function() {
                var self = this;
                this.fetchUserpic($('#user_profile_button').data('username'), function(url) {
                    self.DOM.UserAvatar.css('background-image', 'url(' + url + ')');
                })
            },

            fetchUserpic: function (username, cb) {
                var self = this;
                $.ajax('/api/userpic', {
                    method: 'GET',
                    data: {
                        username: username
                    }
                })
                    .done(function (d) {
                        if (d.status == 401) {
                            window.location.href = d.redirect_url;
                            return;
                        }
                        if (d.status === 200) {
                            console.log('[userpic] loaded');
                            if (cb) {
                                cb(d.url);
                            }
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

            loadInitialRecommendations: function (username, withContent, cb) {
                var self = this;
                cb = cb || function () {};

                this.offset = 0;
                this.loadRecommendations(username, this.limit, this.offset, true, withContent, function (d) {
                    if (withContent) {
                        self.DOM.Loader.remove();
                        self.bindToDOM();
                        self.DOM.MainContentInner.prepend(d.result);
                    }
                    cb(d);
                }, self.loadInitialRecommendations.bind(self, username, withContent, cb));
            },

            loadNextRecommendations: function (username, cb) {
                var self = this;
                cb = cb || function () {};

                this.loadRecommendations(username, this.limit, this.offset, false, false, function (d) {
                    //if (d.count == 0) {
                    //    self.DOM.Loader.hide();
                    //}
                    cb(d);
                }, self.loadNextRecommendations.bind(self, username, cb));
            },

            loadRecommendations: function (username, limit, offset, initial, withContent, cb, funcToRetry) {
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
                        with_content: withContent ? 1 : 0,
                        target_username: username
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
