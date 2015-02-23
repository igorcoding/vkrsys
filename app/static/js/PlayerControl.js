define(['jquery'],
    function($) {
        function PlayerControl(playerId) {
            this.$obj = $(playerId);
            this.DOM = {};
            this.bindToDOM();
            this.registerEvents();

            this.playingSong = null;
            this.state = this.States.Paused;
            this.playlist = null;
        }

        PlayerControl.prototype = {

            C: {
                Art: '.player__art',
                Main: '.player__main',
                Audio: '.player__main__audio',
                MainSong: '.player__main__song',
                MainSongTitle: '.player__main__song__title',
                MainSongProgressBar: '.player__main__song__progressbar',
                MainControls: '.player__main__controls',
                MainControlsDislike: '.player__main__controls__dislike',
                MainControlsPrev: '.player__main__controls__prev',
                MainControlsPlayPause: '.player__main__controls__playpause',
                MainControlsNext: '.player__main__controls__next',
                MainControlsLike: '.player__main__controls__like'
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

                this.DOM.MainSongProgressBar.slider({
                    orientation: "horizontal",
                    range: "min",
                    max: 10000,
                    slide: this.onProgressSlide.bind(this),
                    change: null
                });
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
                window.registerOnResize(this.onWindowResize, this);
                this.onWindowResize(window);
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
                    - 4 - 1; // 4 is for 4 borders by 1px
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

            registerOnRateClick: function () {
                var self = this;
                var like = this.DOM.MainControlsLike;
                var dislike = this.DOM.MainControlsDislike;

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
                var normedTime = audio.currentTime / audio.duration * 10000;
                this.DOM.MainSongProgressBar.slider('value', normedTime);
                if (normedTime === 10000) {
                    this.playlist.next();
                }
            },

            onProgressSlide: function () {
                //var audio = this.DOM.Audio[0];
                //audio.pause();
                //var normedTime = this.DOM.MainSongProgressBar.slider('value');
                //var time = normedTime / 10000 * audio.duration;
                //audio.currentTime = time;
                //audio.play();
            },

            visualPlay: function ($ppButton) {
                if (!$ppButton) {
                    $ppButton = this.DOM.MainControlsPlayPause;
                }
                var playPauseClass = rawC(this.C.MainControlsPlayPause);
                $ppButton.removeClass(playPauseClass + '_paused');
                $ppButton.addClass(playPauseClass + '_playing');
                this.DOM.MainSongTitle.text(this.playingSong.artist + "  -  " + this.playingSong.title);
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
            },

            actualPause: function ($audio) {
                $audio.animate({volume: 0}, 500, function () {
                    $audio[0].pause();
                });
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