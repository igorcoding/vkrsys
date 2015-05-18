define(['jquery', 'toastr'],
    function($, toastr) {
        function UserCard($obj, playlist) {
            if (!$obj) {
                throw '$obj cannot be empty!';
            }
            this.$obj = $obj;
            this.DOM = {};
            this.bindToDOM();
            this.DOM.Entry = this.$obj;

            this.hovering = false;
            this.username = this.DOM.UserpicUsername.text();
            this.playing = false;

            var self = this;
            this.loadUserpic(function(url) {
                console.log(url);
                self.DOM.Userpic.empty();
                self.DOM.Userpic.css(
                    'background-image', 'url(' + url + ')'
                )
            });
            //console.log(this.username);
        }

        UserCard.prototype = {
            C: {
                Entry: '.playlist__entry',
                Userpic: '.user-card__userpic',
                UserpicPlay: '.user-card__userpic__play',
                UserpicDim: '.user-card__userpic__dim',
                UserpicUsername: '.user-card__username'
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

            onWindowResize: function (w, entryInfo) {

            },

            onHoverEnter: function () {
                this.hovering = true;
                if (!this.playing) {
                    this.DOM.UserpicPlay.show();
                    this.DOM.Userpic.addClass('user-card__userpic_hover');
                }
            },

            onHoverLeave: function () {
                this.hovering = false;
                if (!this.playing) {
                    this.DOM.UserpicPlay.hide();
                    this.DOM.Userpic.removeClass('user-card__userpic_hover');
                }
            },

            onClick: function(playerControl) {
                window.TARGET_USERNAME = this.username;
                playerControl.refreshEvent(function() {
                    playerControl.playlist.playFirst();
                });
            },

            startPlaying: function() {
                this.DOM.Userpic.addClass('user-card__userpic_hover');
                this.DOM.UserpicPlay.show();
                this.playing = true;
            },

            stopPlaying: function() {
                this.DOM.Userpic.removeClass('user-card__userpic_hover');
                this.DOM.UserpicPlay.hide();
                this.playing = false;
            },

            loadUserpic: function(cb) {
                window.contentLoader.fetchUserpic(this.username, cb);
            }
        };

        return UserCard;
    }
);

