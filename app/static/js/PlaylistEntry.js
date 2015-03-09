define(['jquery'],
    function($) {
        function PlaylistEntry($obj, playlist) {
            if (!$obj) {
                throw '$obj cannot be empty!';
            }
            this.$obj = $obj;
            this.playlist = playlist;
            this.state = this.States.Paused;
            this.DOM = {};
            this.bindToDOM();
            this.DOM.Entry = this.$obj;
            this.artist = this.DOM.EntryHeaderArtist.text();
            this.title = this.DOM.EntryHeaderTitle.text();
            this.normalizeTextsLengths();
            this.artUrl = this.DOM.EntryArt.data('art_url');
            this.isRated = Boolean(parseInt(this.$obj.data('rated')));

            this.playPauseVisible = this.DOM.EntryControlsPlayPause.css('display') != 'none';
            this.forceShowPlayPause = false;
            this.hovering = false;
        }

        PlaylistEntry.prototype = {
            States: {
                Paused: 'paused',
                Playing: 'playing'
            },

            C: {
                Entry: '.playlist__entry',
                EntryInfo: '.playlist__entry__info',
                EntryArt: '.playlist__entry__info__art',
                EntryHeader: '.playlist__entry__info__header',
                EntryHeaderArtist: '.playlist__entry__title__artist',
                EntryHeaderTitle: '.playlist__entry__title__title',
                EntryControlsPlayPause: '.playlist__entry__controls__playpause',
                EntryControls: '.playlist__entry__controls',
                EntryControlsLikeJs: '.js-playlist__entry__controls__like',
                EntryControlsLike: '.playlist__entry__controls__like',
                EntryControlsDislikeJs: '.js-playlist__entry__controls__dislike',
                EntryControlsDislike: '.playlist__entry__controls__dislike'
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
                entryInfo = entryInfo || this.DOM.EntryInfo;
                var entryArt = entryInfo ? entryInfo.find(this.C.EntryArt) : this.DOM.EntryArt;
                var entryHeader = entryInfo ? entryInfo.find(this.C.EntryHeader) : this.DOM.EntryHeader;
                var entryHeaderMargin = entryHeader.margin();
                //var playPause = entryInfo.find(this.C.EntryControlsPlayPause);
                var likeDislike = entryInfo.find(this.C.EntryControls);

                entryInfo.width(entryInfo.parent().width());

                var minus = entryInfo.width() - entryArt.totalWidth()
                    - entryHeaderMargin.left
                    - entryHeaderMargin.right
                    - 150 - 1;
                entryHeader.width(minus);
            },

            getState: function () {
                return this.state || this.States.Paused;
            },

            _setState: function (state) {
                this.state = state;
            },

            setStatePaused: function () {
                this._setState(this.States.Paused);
            },

            setStatePlaying: function () {
                this._setState(this.States.Playing);
            },

            getSongId: function () {
                return this.$obj.data('song_id') || null;
            },

            setRated: function(rate) {
                this.$obj.data('rated', 1);
                this.DOM.EntryControlsLikeJs.removeClass(rawC(this.C.EntryControlsLike));
                this.DOM.EntryControlsDislikeJs.removeClass(rawC(this.C.EntryControlsDislike));

                if (rate === 'up') {
                    this.DOM.EntryControlsLikeJs.addClass(rawC(this.C.EntryControlsLike) + '_active');
                    this.DOM.EntryControlsDislikeJs.addClass(rawC(this.C.EntryControlsDislike) + '_inactive');
                    this.playlist.playerControl.applyRate(1);
                } else if (rate === 'down') {
                    this.DOM.EntryControlsLikeJs.addClass(rawC(this.C.EntryControlsLike) + '_inactive');
                    this.DOM.EntryControlsDislikeJs.addClass(rawC(this.C.EntryControlsDislike) + '_active');
                    this.playlist.playerControl.applyRate(0);
                }
            },

            getRating: function() {
                return this.$obj.data('rating');
            },

            normalizeTextsLengths: function() {
                var max = 60;
                var ellipsis = '<span class="ellipsis">...</span>';
                if (this.artist.length > max) {
                    this.DOM.EntryHeaderArtist.html(this.artist.slice(0, max+1) + ellipsis);
                    this.DOM.EntryHeaderArtist.attr("alt", this.artist);
                }

                if (this.title.length > max) {
                    this.DOM.EntryHeaderTitle.html(this.title.slice(0, max+1) + ellipsis);
                    this.DOM.EntryHeaderTitle.attr("alt", this.title);
                }
            },

            onHoverEnter: function () {
                this.hovering = true;
                this.DOM.EntryControls.show();
                this.displayPlayPause();
            },

            onHoverLeave: function () {
                this.hovering = false;
                this.DOM.EntryControls.hide();
                this.hidePlayPause();
            },

            displayPlayPause: function() {
                if (!this.playPauseVisible) {
                    this.DOM.EntryControlsPlayPause.show();
                    this.DOM.EntryArt.addClass('playlist__entry__info__art_dimmed');
                    this.playPauseVisible = true;
                }
            },

            hidePlayPause: function() {
                if (this.playPauseVisible && !this.forceShowPlayPause) {
                    this.DOM.EntryControlsPlayPause.hide();
                    this.DOM.EntryArt.removeClass('playlist__entry__info__art_dimmed');
                    this.playPauseVisible = false;
                }
            },

            visualPause: function () {
                var $playPause = this.DOM.EntryControlsPlayPause;
                var ppClass = rawC(this.C.EntryControlsPlayPause);
                var entryClass = rawC(this.C.Entry);
                $playPause.removeClass(ppClass + '_playing');
                $playPause.addClass(ppClass + '_paused');

                this.$obj.removeClass(entryClass + '_playing');
                this.$obj.addClass(entryClass + '_paused');

                this.setStatePaused();
                this.forceShowPlayPause = false;
                if (!this.hovering) {
                    this.hidePlayPause();
                }
            },

            visualPlay: function () {
                var $playPause = this.DOM.EntryControlsPlayPause;
                var ppClass = rawC(this.C.EntryControlsPlayPause);
                var entryClass = rawC(this.C.Entry);
                $playPause.removeClass(ppClass + '_paused');
                $playPause.addClass(ppClass + '_playing');
                this.$obj.removeClass(entryClass + '_hover');
                this.$obj.removeClass(entryClass + '_paused');
                this.$obj.addClass(entryClass + '_playing');

                this.setStatePlaying();
                this.forceShowPlayPause = true;
                this.displayPlayPause();
            },

            play: function () {
                this.visualPlay();
            },

            pause: function () {
                this.visualPause();
            },

            rate: function (direction) {
                var self = this;
                if (this.isRated) {
                    alert('not possible');
                    // TODO: may be some sort of notification
                    return;
                }

                if (direction !== 'up' && direction !== 'down') {
                    console.warn('Unknown direction: ' + direction);
                    return;
                }
                $.ajax('/api/rate', {
                    method: 'GET', // TODO: should be POST
                    data: {
                        song_id: this.getSongId(),
                        direction: direction
                    }
                })
                    .done(function (data) {
                        console.log(data);
                        self.setRated(direction);
                        self.isRated = true;
                    })
                    .fail(function (data) {
                        console.warn(data);
                    });
            },

            like: function () {
                this.rate('up');
            },

            dislike: function () {
                this.rate('down');
            }
        };

        return PlaylistEntry;
    }
);

