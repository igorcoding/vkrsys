define(['jquery', 'toastr', 'UserCard'],
    function($, toastr, UserCard) {
        function UsersCards(usersCardsId) {
            this.$obj = $(usersCardsId);
            this.DOM = {};
            this.bindToDOM();
            this.$cards = null;
            this.cards = [];

            this.playerControl = null;

            this.limit = 30;
            this.offset = 0;
            this.initial = true;
            this.loading = true;

            this.currentPlayingCard = null;
            this.stopLoading = false;
            this.registerEvents();
        }

        UsersCards.prototype = {
            C: {

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

            setPlayerControl: function(playerControl) {
                this.playerControl = playerControl;
            },

            addContent: function(d) {
                var $newCards = $(d.result);
                $newCards = $newCards.filter(function(n) {return ($newCards[n].nodeType != 3)});
                this.$obj.append($newCards);
                this.exploreEntries($newCards);
            },

            replaceContent: function(d) {
                this.$obj.empty();
                this.addContent(d);
            },

            exploreEntries: function($cards) {
                var self = this;
                console.log($cards.length);
                $cards.each(function() {
                    var $this = $(this);
                    self.cards.push(new UserCard($this));
                    var last = self.cards[self.cards.length - 1];
                    $this.hover(UserCard.prototype.onHoverEnter.bind(last), UserCard.prototype.onHoverLeave.bind(last));
                    $this.click();
                    $this.click(function() {
                        var selected = last;
                        if (self.currentPlayingCard) {
                            if (selected == self.currentPlayingCard) {

                            } else {
                                self.currentPlayingCard.stopPlaying();
                                self.currentPlayingCard = selected;
                                self.currentPlayingCard.startPlaying();
                                self.currentPlayingCard.onClick(self.playerControl);
                            }
                        } else {
                            self.currentPlayingCard = selected;
                            self.currentPlayingCard.startPlaying();
                            self.currentPlayingCard.onClick(self.playerControl);
                        }
                    });
                });
                this.$cards = $(UserCard.prototype.C.Entry);
            },

            isVisible: function() {
                return this.$obj.is(':visible');
            },

            show: function() {
                this.$obj.show();
            },

            hide: function() {
                this.$obj.hide();
            },


            onWindowResize: function (w, entryInfo) {

            },

            stopPlaying: function() {
                this.currentPlayingCard.stopPlaying();
            },

            registerEvents: function() {
                var self = this;
                this.$obj.scroll(function() {
                    if(!self.loading && !self.stopLoading && Math.ceil(self.$obj.scrollTop()) >= self.$obj.prop('scrollHeight') - self.$obj.height() - 100) {
                        self.loadCards();
                        console.log("loading more users");
                    }
                });
            },

            loadCards: function() {
                var self = this;
                this.load(function(d) {
                    if (d.count == 0) {
                        self.stopLoading = true;
                    }
                    if (self.initial) {
                        self.replaceContent(d);
                        self.initial = false;
                    } else {
                        self.addContent(d);
                    }
                });
            },

            load: function(cb) {
                var self = this;
                this.loading = true;
                $.ajax('/api/users', {
                    method: 'GET',
                    data: {
                        limit: this.limit,
                        offset: this.offset
                    }
                })
                    .done(function (d) {
                        self.loading = false;
                        if (d.status == 401) {
                            window.location.href = d.redirect_url;
                            return;
                        }
                        if (d.status == 200) {
                            self.offset += d.count;

                            cb(d);
                        } else {
                            //retrial(500);
                        }
                    })
                    .fail(function (d) {
                        self.loading = false;
                        console.warn('[users cards] disaster: ', d);
                        //retrial(2000);
                    });
            }
        };

        return UsersCards;
    }
);
