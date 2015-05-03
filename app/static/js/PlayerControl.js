define(['jquery', 'PlayerProgressbar'],
    function($, PlayerProgressbar) {
        function PlayerControl(playerId) {
            this.$obj = $(playerId);
            this.DOM = {};
            this.bindToDOM();
            this.registerEvents();

            this.playingSong = null;
            this.state = this.States.Paused;
            this.playlist = null;

            this.SLIDER_MAX = 100000;
            this.progressBar = new PlayerProgressbar(this.DOM.ProgressBar, this.SLIDER_MAX);
            this.progressBar.addOnProgressChangedManuallyListener(this.onManualSlide.bind(this));
            this.defaultDocumentTitle = document.title;
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
                ProgressBar: '.player__progressbar'
            },

            States: {
                Paused: 'paused',
                Playing: 'playing'
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

            getState: function () {
                return this.state;
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

            getPlaylist: function () {
                if (this.playlist) {
                    return this.playlist;
                }
                throw "Playlist is null";
            },

            setPlaylist: function (playlist) {
                this.playlist = playlist;
            },

            registerEvents: function () {
                //window.registerOnResize(this.onWindowResize, this);
                //this.onWindowResize(window);
                this.registerOnPlayClick();
                this.registerOnPrevNextClick();
                this.registerOnRateClick();
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

            registerOnPlayClick: function () {
                var self = this;
                var playPause = this.DOM.MainControlsPlayPause;

                playPause.click(function () {
                    var $this = $(this);
                    if (self.getState() === self.States.Playing) {
                        self.visualPause($this);
                        self.pause(true);
                    } else {
                        //self.visualPlay($this);
                        self.play();
                    }
                });
            },

            registerOnPrevNextClick: function () {
                var self = this;
                var prev = this.DOM.MainControlsPrev;
                var next = this.DOM.MainControlsNext;

                prev.click(function () {
                    self.playlist.prev();
                });

                next.click(function () {
                    self.playlist.next();
                });
            },

            applyRate: function(rating) {
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
                console.log("rating", rating);
            },

            registerOnRateClick: function () {
                var self = this;
                var like = this.DOM.MainControlsLikeJs;
                var dislike = this.DOM.MainControlsDislikeJs;

                like.click(function () {
                    if (self.playingSong) {
                        self.playingSong.like();
                    }
                });

                dislike.click(function () {
                    if (self.playingSong) {
                        self.playingSong.dislike();
                    }
                });
            },


            registerAudioEvents: function () {
                var self = this;
                var $audio = this.DOM.Audio;
                var audio = $audio[0];
                audio.ontimeupdate = function () {
                    self.onAudioTimeUpdate(audio);
                };
            },

            onAudioTimeUpdate: function (audio) {
                if (!this.progressManualSliding) {
                    if (this.prevAudioTime == -1) {
                        this.prevAudioTime = audio.currentTime;
                    }
                    if (!this.afterManualSlide) {
                        this.playingSong.listenedDuration += audio.currentTime - this.playingSong.lastListenedTime;
                        this.playingSong.characterise();
                    }

                    //console.log(this.playingSong.listenedDuration);
                    var normedTime = audio.currentTime / audio.duration * this.SLIDER_MAX;
                    if (!this.progressBar.isChangingManually()) {
                        this.progressBar.changeProgress(normedTime);
                    }
                    //this.DOM.MainSongProgressBar.slider('value', normedTime);
                    if (normedTime === this.SLIDER_MAX) {
                        this.playlist.next();
                    }

                    this.playingSong.lastListenedTime = audio.currentTime;
                    this.afterManualSlide = false;
                }
            },

            onProgressSlideStart: function(event, ui) {
                this.progressManualSliding = true;
            },

            onProgressSlideStop: function(event, ui) {

            },

            onManualSlide: function(progress) {
                //if (this.progressManualSliding) {
                    var audio = this.DOM.Audio[0];
                    audio.currentTime = progress / this.SLIDER_MAX * audio.duration;
                    //this.progressManualSliding = false;
                    //this.afterManualSlide = true;
                //}
            },

            initRateButtons: function() {
                if (this.playingSong.isRated()) {
                    var rating = this.playingSong.getRating();
                    this.applyRate(rating);
                } else {
                    this.DOM.MainControlsLikeJs.removeClass(rawC(this.C.MainControlsLike) + '_inactive');
                    this.DOM.MainControlsLikeJs.removeClass(rawC(this.C.MainControlsLike) + '_active');
                    this.DOM.MainControlsDislikeJs.removeClass(rawC(this.C.MainControlsDislike) + '_inactive');
                    this.DOM.MainControlsDislikeJs.removeClass(rawC(this.C.MainControlsDislike) + '_active');

                    this.DOM.MainControlsLikeJs.addClass(rawC(this.C.MainControlsLike));
                    this.DOM.MainControlsDislikeJs.addClass(rawC(this.C.MainControlsDislike));
                }
            },

            initPlay: function() {
                var $ppButton = this.DOM.MainControlsPlayPause;
                var playPauseClass = rawC(this.C.MainControlsPlayPause);
                $ppButton.removeClass(playPauseClass + '_paused');
                $ppButton.addClass(playPauseClass + '_playing');
                this.DOM.MainSongArtist.text(this.playingSong.artist);
                this.DOM.MainSongTitle.text(this.playingSong.title);
                this.DOM.Art.css({
                    'background-image': 'url(' + this.playingSong.artUrl + ')'
                });
                this.initRateButtons();
            },

            visualPlay: function () {
                this.initPlay();
                this.setStatePlaying();
            },


            visualPause: function ($ppButton) {
                if (!$ppButton) {
                    $ppButton = this.DOM.MainControlsPlayPause;
                }
                var playPauseClass = rawC(this.C.MainControlsPlayPause);
                $ppButton.removeClass(playPauseClass + '_playing');
                $ppButton.addClass(playPauseClass + '_paused');
                this.setStatePaused();
            },

            actualPlay: function ($audio) {
                $audio[0].volume = 0;
                $audio[0].play();
                $audio.animate({volume: 1}, 500, function () {

                });
                document.title = this.playingSong.title + " - " + this.playingSong.artist;
            },

            actualPause: function ($audio) {
                this.playingSong.characterise(true);
                $audio.animate({volume: 0}, 500, function () {
                    $audio[0].pause();
                });
                document.title = this.defaultDocumentTitle;
            },

            play: function (song_entry) {
                var self = this;
                var $audio = this.DOM.Audio;
                var audio = $audio[0];

                var song_id = song_entry ? song_entry.getSongId() : undefined;
                if (!song_id && !this.playingSong) {
                    this.playlist.playFirst();
                    return;
                } else if (!song_id) {
                    this.visualPlay();
                    this.playlist.playingEntry.play();
                }
                if (!song_id || this.playingSong && song_id === this.playingSong.getSongId()) {  // continue playing
                    console.log("[Player] continuing");
                    this.visualPlay();
                    this.actualPlay($audio);
                    //audio.onloadeddata = function() {
                    //    audio.play();
                    //};
                    //audio.load();

                } else {  // new song
                    console.log("[Player] new song");
                    // fetch audio url
                    this.fetchAudioUrl(song_id, function (url) {
                        self.playingSong = song_entry;
                        self.visualPlay();
                        audio.src = url;
                        audio.onloadeddata = function () {
                            self.progressBar.resetProgress();
                            self.actualPlay($audio);
                        };
                        audio.load();
                    });
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
                console.log(song_id);
                $.ajax('/api/song_url', {
                    method: 'GET',
                    data: {
                        song_id: song_id
                    }
                })
                    .done(function (d) {
                        if (d.redirect) {
                            window.location.href = d.redirect;
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