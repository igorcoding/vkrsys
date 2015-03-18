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

            this.playPauseVisible = this.DOM.EntryControlsPlayPause.css('display') != 'none';
            this.forceShowPlayPause = false;
            this.hovering = false;

            this.id = this.getSongId();
            this.hops_count = 0;
            this.lastListenedTime = 0;
            this.listenedDuration = 0;
            this.duration = 0;
            this.characteriseDelayMax = 50;
            this.characteriseDelay = this.characteriseDelayMax;
            this.countDuration();
        }

        PlaylistEntry.prototype = {
            States: {
                Paused: 'paused',
                Playing: 'playing'
            },

            C: {
                Entry: '.playlist__entry',
                EntryInfo: '.playlist__entry__info',
                EntryDuration: '.playlist__entry__duration',
                EntryArt: '.playlist__entry__info__art',
                EntryHeader: '.playlist__entry__info__header',
                EntryHeaderArtist: '.playlist__entry__title__artist',
                EntryHeaderTitle: '.playlist__entry__title__title',
                EntryControlsPlayPause: '.playlist__entry__controls__playpause',
                EntryControls: '.playlist__entry__controls',
                EntryControlsLikeJs: '.js-playlist__entry__controls__like',
                EntryControlsLike: '.playlist__entry__controls__like',
                EntryControlsDislikeJs: '.js-playlist__entry__controls__dislike',
                EntryControlsDislike: '.playlist__entry__controls__dislike',
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
                this.$obj.data('rated', '1');
                this.DOM.EntryControlsLikeJs.removeClass(rawC(this.C.EntryControlsLike));
                this.DOM.EntryControlsDislikeJs.removeClass(rawC(this.C.EntryControlsDislike));

                if (rate === 'up') {
                    this.DOM.EntryControlsLikeJs.addClass(rawC(this.C.EntryControlsLike) + '_active');
                    this.DOM.EntryControlsDislikeJs.addClass(rawC(this.C.EntryControlsDislike) + '_inactive');
                    this.playlist.playerControl.applyRate(1);
                    this.setRating(1);
                } else if (rate === 'down') {
                    this.DOM.EntryControlsLikeJs.addClass(rawC(this.C.EntryControlsLike) + '_inactive');
                    this.DOM.EntryControlsDislikeJs.addClass(rawC(this.C.EntryControlsDislike) + '_active');
                    this.playlist.playerControl.applyRate(0);
                    this.setRating(0);
                }
            },

            getRating: function() {
                return this.$obj.data('rating');
            },

            setRating: function(rating) {
                this.$obj.data('rating', rating);
            },

            isRated: function() {
                return Boolean(parseInt(this.$obj.data('rated')));
            },

            normalizeTextsLengths: function() {
                var max = 50;
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

            countDuration: function() {
                this.duration = parseInt(this.DOM.EntryDuration.text());
                this.DOM.EntryDuration.text(this.durationToTime());
            },

            durationToTime: function() {
                var minutes = Math.floor(this.duration / 60);
                var seconds = this.duration - minutes * 60;
                if (seconds < 10) {
                    seconds = "0" + String(seconds);
                }
                return minutes + ":" + seconds;
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

            waitForCharacteriseDelay: function(force) {
                if (force) {
                    this.characteriseDelay = this.characteriseDelayMax;
                    return true;
                }
                if (--this.characteriseDelay > 0) {
                    return false;
                } else {
                    this.characteriseDelay = this.characteriseDelayMax;
                    return true;
                }
            },

            characterise: function(force) {
                if (this.waitForCharacteriseDelay(force)) {
                    var self = this;
                    $.ajax('/api/characterise', {
                        method: 'POST',
                        contentType: "application/json",
                        data: JSON.stringify({
                            song_id: this.id,
                            hops_count: this.hops_count,
                            duration: this.listenedDuration
                        })
                    })
                        .done(function (data) {
                            console.log(data);
                        })
                        .fail(function (data) {
                            console.warn(data);
                        });
                }
            },

            rate: function (direction) {
                var self = this;
                if (this.isRated()) {
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

