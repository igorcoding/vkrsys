define(['jquery', 'PlayerApp/Playlist', 'PlayerApp/PlayerProgressbar', 'PlayerApp/Keyboard', 'Util'],
    function($, Playlist, PlayerProgressbar, Keyboard, Util) {
        function PlayerControl(playerId, playlist, usersCards, contentLoader, keyboardBindings) {
            this.$obj = $(playerId);
            this.contentLoader = contentLoader;
            this.keyboardBindingsActionToCh = keyboardBindings;
            this.keyboardBindingsChToAction = Util.inverseObject(keyboardBindings);
            this.keyboardEnabled = true;
            this.DOM = {};
            this.bindToDOM();
            this.initTooltips();
            this.registerEvents();

            this.playlist = playlist;
            this.playlistVisible = this.playlist.isVisible();
            this.playingSong = this.playlist.setPlaying(0);
            this.initRateButtons();

            this.usersCards = usersCards;
            this.usersCardsVisible = this.usersCards.isVisible();

            this.prevState = null;
            this.state = this.States.Stopped;

            this.afterManualSlide = false;
            this.SLIDER_MAX = 100000;
            var firstEntry = this.playlist.entries[0];
            this.progressBar = new PlayerProgressbar(this.DOM.ProgressBar, this.SLIDER_MAX);
            this.progressBar.addOnProgressChangedManuallyListener(this.onManualSlide.bind(this));
            this.progressBar.addOnProgressChangingManuallyListener(this.onManualSlideInProgress.bind(this));
            this.progressBar.setMaxProgressText(firstEntry.durationToTime(firstEntry.duration));
            this.progressBar.reactToSlide = false;
            this.defaultDocumentTitle = document.title;

            this.AUDIO_VOLUME_ANIMATION_SPEED = 500;
        }

        PlayerControl.prototype = {

            C: {
                Art: '.player__main__song__art',
                Main: '.player__main',
                Audio: '.player__main__audio',
                MainSong: '.player__main__song',
                MainSongArtist: '.player__main__song__artist',
                MainSongTitle: '.player__main__song__title',
                MainControls: '.player__main__controls',
                MainControlsPrev: '.player__main__controls__prev',
                MainControlsPlayPause: '.player__main__controls__playpause',
                MainControlsNext: '.player__main__controls__next',
                MainControlsDislikeJs: '.js-player__main__ratecontrols__dislike',
                MainControlsDislike: '.player__main__ratecontrols__dislike',
                MainControlsLikeJs: '.js-player__main__ratecontrols__like',
                MainControlsLike: '.player__main__ratecontrols__like',
                MainControlsTogglePlaylist: '.player__main__toggle-playlist',
                MainControlsRefresh: '.player__main__refresh-button',
                ProgressBar: '.player__progressbar'
            },

            States: {
                Paused: 'paused',
                Playing: 'playing',
                Stopped: 'stopped'
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

            initTooltips: function() {
                var self = this;
                var makeTitle = function(control, action, initialText) {
                    var text = initialText;
                    var kb = self.keyboardBindingsActionToCh[action];
                    if (kb) {
                        text += " [" + kb.toUpperCase() + "]"
                    }
                    control.attr('title', text);
                };
                makeTitle(this.DOM.MainControlsPlayPause, 'playpause', gettext('Play/Pause'));
                makeTitle(this.DOM.MainControlsPrev, 'prev', gettext('Previous'));
                makeTitle(this.DOM.MainControlsNext, 'next', gettext('Next'));
                makeTitle(this.DOM.MainControlsLike, 'like', gettext('Like'));
                makeTitle(this.DOM.MainControlsDislike, 'dislike', gettext('Dislike'));
                makeTitle(this.DOM.MainControlsRefresh, 'refresh', gettext('Refresh'));
                makeTitle(this.DOM.MainControlsTogglePlaylist, 'toggle', gettext('Toggle playlist'));
            },

            getState: function () {
                return this.state;
            },

            getPrevState: function () {
                return this.prevState;
            },

            _setState: function (state) {
                this._setPrevState(this.state);
                this.state = state;
            },

            _setPrevState: function (prevState) {
                this.prevState = prevState;
            },

            setStatePaused: function () {
                this._setState(this.States.Paused);
            },

            setStatePlaying: function () {
                this._setState(this.States.Playing);
            },

            setStateStopped: function () {
                this._setState(this.States.Stopped);
            },

            getPlaylist: function () {
                if (this.playlist) {
                    return this.playlist;
                }
                throw "Playlist is null";
            },

            registerEvents: function () {
                //window.registerOnResize(this.onWindowResize, this);
                //this.onWindowResize(window);
                this.registerClickEvents();
                this.registerKeyboardEvents();
                this.registerAudioEvents();
            },

            onWindowResize: function (w) {
                var playerMainMargin = this.DOM.Main.margin();
                var mainWidth = this.$obj.width()
                    - this.DOM.Art.totalWidth()
                    - playerMainMargin.left
                    - playerMainMargin.right
                    - 4 - 2; // 4 is for 4 borders by 1px
                this.DOM.Main.width(mainWidth);
            },

            playPauseButtonEvent: function(forcePlay) {
                if (this.getState() === this.States.Playing) {
                    this.pause(true);
                } else {
                    this.play();
                }
            },

            prevButtonEvent: function() {
                var audio = this.DOM.Audio[0];
                if (this.getState() == this.States.Playing && audio.currentTime > 10) {
                    audio.currentTime = 0;
                } else {
                    this.playlist.prev();
                }
            },

            nextButtonEvent: function() {
                this.playlist.next();
            },

            likeButtonEvent: function() {
                if (this.playingSong) {
                    this.playingSong.like();
                }
            },

            dislikeButtonEvent: function() {
                if (this.playingSong) {
                    this.playingSong.dislike();
                }
            },

            refreshEvent: function(cb) {
                var self = this;
                contentLoader.loadInitialRecommendations(window.TARGET_USERNAME, false, function(d) {
                    self.playlist.replaceContent(d);
                    self.playlist.scrollTo(0);
                    if (cb) {
                        cb();
                    } else {
                        self.usersCards.stopPlaying();
                    }

                });
            },

            togglePlaylistEvent: function() {
                var self = this;
                if (this.playlistVisible) {
                    //this.$obj.css({height: 0});
                    this.playlist.hide();
                    this.usersCards.show();
                } else {
                    //this.$obj.css({height: '100%'});
                    //this.DOM.Playlist.closest().show();
                    this.playlist.show();
                    this.usersCards.hide();
                }
                this.playlistVisible = !this.playlistVisible;
                this.usersCardsVisible = !this.usersCardsVisible;
            },

            registerClickEvents: function () {
                var self = this;

                var playPause = this.DOM.MainControlsPlayPause;
                var prev = this.DOM.MainControlsPrev;
                var next = this.DOM.MainControlsNext;
                var like = this.DOM.MainControlsLikeJs;
                var dislike = this.DOM.MainControlsDislikeJs;
                var refresh = this.DOM.MainControlsRefresh;
                var togglePlaylist = this.DOM.MainControlsTogglePlaylist;

                playPause.click(this.playPauseButtonEvent.bind(this));
                prev.click(this.prevButtonEvent.bind(this));
                next.click(this.nextButtonEvent.bind(this));
                like.click(this.likeButtonEvent.bind(this));
                dislike.click(this.dislikeButtonEvent.bind(this));
                refresh.click(function() {
                    self.refreshEvent();
                });
                togglePlaylist.click(this.togglePlaylistEvent.bind(this));
            },

            registerKeyboardEvents: function() {
                var self = this;
                $(window).keypress(function(e) {
                    if (self.keyboardEnabled) {
                        var ch = Keyboard.getChar(e).toLowerCase();
                        if (ch != null && self.keyboardBindingsChToAction && self.keyboardBindingsChToAction.hasOwnProperty(ch)) {
                            var b = self.keyboardBindingsChToAction[ch];
                            var f = null;
                            switch (b) {
                                case "playpause":
                                    f = self.playPauseButtonEvent.bind(self);
                                    break;
                                case "next":
                                    f = self.nextButtonEvent.bind(self);
                                    break;
                                case "prev":
                                    f = self.prevButtonEvent.bind(self);
                                    break;
                                case "like":
                                    f = self.likeButtonEvent.bind(self);
                                    break;
                                case "dislike":
                                    f = self.dislikeButtonEvent.bind(self);
                                    break;
                                case "refresh":
                                    f = self.refreshEvent.bind(self);
                                    break;
                                case "toggle":
                                    f = self.togglePlaylistEvent.bind(self);
                                    break;
                            }
                            if (f) {
                                f();
                            }
                        }
                    }
                });
            },

            enableKeyboardEvents: function() {
                this.keyboardEnabled = true;
            },

            disableKeyboardEvents: function() {
                this.keyboardEnabled = false;
            },

            applyRate: function(entry, rating) {
                if (this.playingSong && this.playingSong.getSongId() == entry.getSongId()) {
                    this.DOM.MainControlsLikeJs.removeClass(rawC(this.C.MainControlsLike));
                    this.DOM.MainControlsDislikeJs.removeClass(rawC(this.C.MainControlsDislike));
                    this.DOM.MainControlsLikeJs.removeClass(rawC(this.C.MainControlsLike) + '_inactive');
                    this.DOM.MainControlsLikeJs.removeClass(rawC(this.C.MainControlsLike) + '_active');
                    this.DOM.MainControlsDislikeJs.removeClass(rawC(this.C.MainControlsDislike) + '_inactive');
                    this.DOM.MainControlsDislikeJs.removeClass(rawC(this.C.MainControlsDislike) + '_active');

                    if (rating == 1) {
                        this.DOM.MainControlsLikeJs.addClass(rawC(this.C.MainControlsLike) + '_active');
                        this.DOM.MainControlsDislikeJs.addClass(rawC(this.C.MainControlsDislike) + '_inactive');
                    } else if (rating == 0) {
                        this.DOM.MainControlsLikeJs.addClass(rawC(this.C.MainControlsLike) + '_inactive');
                        this.DOM.MainControlsDislikeJs.addClass(rawC(this.C.MainControlsDislike) + '_active');
                    } else {
                        this.DOM.MainControlsLikeJs.addClass(rawC(this.C.MainControlsLike));
                        this.DOM.MainControlsDislikeJs.addClass(rawC(this.C.MainControlsDislike));
                    }
                }
            },

            normalizeTextsLengths: function() {
                var max = 80;
                var ellipsis = '<span class="ellipsis">...</span>';
                if (this.playingSong.artist.length > max) {
                    this.DOM.MainSongArtist.html(this.playingSong.artist.slice(0, max+1) + ellipsis);
                    this.DOM.MainSongArtist.attr("title", this.playingSong.artist);
                }

                if (this.playingSong.title.length > max) {
                    this.DOM.MainSongTitle.html(this.playingSong.title.slice(0, max+1) + ellipsis);
                    this.DOM.MainSongTitle.attr("title", this.playingSong.title);
                }
            },

            registerAudioEvents: function () {
                var self = this;
                var $audio = this.DOM.Audio;
                var audio = $audio[0];
                audio.ontimeupdate = function () {
                    self.onAudioTimeUpdate(audio);
                };
            },

            audioToProgress: function(audio) {
                return audio.currentTime / audio.duration * this.SLIDER_MAX;
            },

            progressToAudio: function(progress) {
                return progress / this.SLIDER_MAX * this.DOM.Audio[0].duration;
            },

            onAudioTimeUpdate: function (audio) {
                if (!this.afterManualSlide) {
                    var cur = audio.currentTime,
                        prev = this.playingSong.lastListenedTime;
                    if (cur < prev) {
                        prev = this.playingSong.lastListenedTime = 0;
                    }
                    this.playingSong.listenedDuration += cur - prev;
                    this.playingSong.characterise();
                }

                var progress = this.audioToProgress(audio);
                this.progressBar.setProgressText(this.playingSong.durationToTime(audio.currentTime));
                if (!this.progressBar.isChangingManually()) {
                    this.progressBar.changeProgress(progress);
                }

                if (progress === this.SLIDER_MAX) {
                    this.playlist.next();
                }

                this.playingSong.lastListenedTime = audio.currentTime;
                this.afterManualSlide = false;
            },

            onManualSlide: function(progress) {
                if (this.playingSong) {
                    var audio = this.DOM.Audio[0];
                    audio.currentTime = this.progressToAudio(progress);
                    this.progressBar.setProgressText(this.playingSong.durationToTime(audio.currentTime));
                    this.afterManualSlide = true;
                }
            },

            onManualSlideInProgress: function(progress) {
                if (this.playingSong) {
                    this.progressBar.setProgressText(this.playingSong.durationToTime(this.progressToAudio(progress)));
                }
            },

            initRateButtons: function() {
                if (this.playingSong.isRated()) {
                    var rating = this.playingSong.getRating();
                    this.applyRate(this.playingSong, rating);
                } else {
                    this.DOM.MainControlsLikeJs.removeClass(rawC(this.C.MainControlsLike) + '_inactive');
                    this.DOM.MainControlsLikeJs.removeClass(rawC(this.C.MainControlsLike) + '_active');
                    this.DOM.MainControlsDislikeJs.removeClass(rawC(this.C.MainControlsDislike) + '_inactive');
                    this.DOM.MainControlsDislikeJs.removeClass(rawC(this.C.MainControlsDislike) + '_active');

                    this.DOM.MainControlsLikeJs.addClass(rawC(this.C.MainControlsLike));
                    this.DOM.MainControlsDislikeJs.addClass(rawC(this.C.MainControlsDislike));
                }
            },

            visualPlay: function () {
                var $ppButton = this.DOM.MainControlsPlayPause;
                var playPauseClass = rawC(this.C.MainControlsPlayPause);
                $ppButton.removeClass(playPauseClass + '_paused');
                $ppButton.addClass(playPauseClass + '_playing');
                this.DOM.MainSongArtist.text(this.playingSong.artist);
                this.DOM.MainSongTitle.text(this.playingSong.title);
                this.DOM.Art.attr("src", this.playingSong.artUrl);
                this.initRateButtons();
                this.normalizeTextsLengths();
            },

            visualPause: function ($ppButton) {
                if (!$ppButton) {
                    $ppButton = this.DOM.MainControlsPlayPause;
                }
                var playPauseClass = rawC(this.C.MainControlsPlayPause);
                $ppButton.removeClass(playPauseClass + '_playing');
                $ppButton.addClass(playPauseClass + '_paused');
            },

            actualPlay: function ($audio) {
                var self = this;
                $audio[0].volume = 0;
                $audio[0].play();
                this.setStatePlaying();
                self.playlist.playingEntry.play();
                $audio.stop().animate({volume: 1}, this.AUDIO_VOLUME_ANIMATION_SPEED, function () {
                    self.playlist.scrollToCurrent();
                    document.title = self.playingSong.title + " - " + self.playingSong.artist;
                });
            },

            actualPause: function ($audio) {
                var self = this;
                this.setStatePaused();
                $audio.stop().animate({volume: 0}, this.AUDIO_VOLUME_ANIMATION_SPEED, function () {
                    $audio[0].pause();
                    self.playingSong.characterise(true);
                    document.title = self.defaultDocumentTitle;
                });
            },

            play: function (song_entry, forcePlay) {
                var self = this;
                var $audio = this.DOM.Audio;
                var audio = $audio[0];

                song_entry = song_entry || this.playingSong;
                var song_id = song_entry ? song_entry.getSongId() : this.playingSong.getSongId();

                if (this.getState() == this.States.Stopped || forcePlay || song_id != this.playingSong.getSongId()) {
                    console.log("[Player] new song");
                    this.playingSong = song_entry;
                    this.fetchAudioUrl(song_id, function (url) {
                        self.progressBar.reactToSlide = true;
                        self.visualPlay();
                        audio.src = url;
                        audio.onloadeddata = function () {
                            self.progressBar.resetProgress();
                            self.progressBar.setMaxProgressText(self.playingSong.durationToTime(self.playingSong.duration));
                            self.actualPlay($audio);
                        };
                        audio.load();
                        audio.play();
                    });
                } else if (song_id == this.playingSong.getSongId()) {
                    console.log("[Player] continuing");
                    this.visualPlay();
                    this.actualPlay($audio);
                }
            },

            pause: function (stopPlaylist) {
                this.visualPause();
                if (stopPlaylist) {
                    this.playlist.pauseCurrent();
                }

                var $audio = this.DOM.Audio;
                this.actualPause($audio);
                console.log("[Player] pause");
            },

            fetchAudioUrl: function (song_id, cb) {
                //console.log(song_id);
                $.ajax('/api/song_url', {
                    method: 'GET',
                    data: {
                        song_id: song_id
                    }
                })
                    .done(function (d) {
                        if (d.status == 401) {
                            window.location.href = d.redirect_url;
                            return;
                        }
                        cb(d['url']);
                    })
                    .fail(function (d) {
                        console.warn(d);
                    });
            }


        };

        return PlayerControl;
    }
);