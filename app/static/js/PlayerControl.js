function PlayerControl(playerId) {
    this.$obj = $(playerId);
    this.DOM = {};
    this.bindToDOM();
    this.registerEvents();

    this.playingSongId = null;
    this.state = this.States.Paused;
    this.playlist = null;
}

PlayerControl.prototype.getPlaylist = function() {
    if (this.playlist) {
        return this.playlist;
    }
    throw "Playlist is null";
};

PlayerControl.prototype.setPlaylist = function(playlist) {
    this.playlist = playlist;
};

PlayerControl.prototype.States = {
    Paused: 'paused',
    Playing: 'playing'
};

PlayerControl.prototype.getState = function() {
    return this.state;
};

PlayerControl.prototype._setState = function(state) {
    this.state = state;
};

PlayerControl.prototype.setStatePaused = function() {
    this._setState(this.States.Paused);
};

PlayerControl.prototype.setStatePlaying = function() {
    this._setState(this.States.Playing);
};

PlayerControl.prototype.C = {
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
};

PlayerControl.prototype.bindToDOM = function() {
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
};

PlayerControl.prototype.registerEvents = function() {
    window.registerOnResize(this.onWindowResize, this);
    this.onWindowResize(window);
    this.registerOnPlayClick();
    this.registerAudioEvents();
};

PlayerControl.prototype.onWindowResize = function(w) {
    var playerMainMargin = this.DOM.Main.margin();
    var mainWidth = this.$obj.width()
                                - this.DOM.Art.totalWidth()
                                - playerMainMargin.left
                                - playerMainMargin.right
                                - 4 - 10; // 4 is for 4 borders by 1px
    this.DOM.Main.width(mainWidth);
};

PlayerControl.prototype.registerOnPlayClick = function() {
    var self = this;
    var playPause = this.DOM.MainControlsPlayPause;

    playPause.click(function() {
        var $this = $(this);
        if (self.getState() === self.States.Playing) {
            self.visualPause($this);
            self.pause(true);
        } else {
            self.visualPlay($this);
            self.play();
        }
    });
};


PlayerControl.prototype.registerAudioEvents = function() {
    var self = this;
    var $audio = this.DOM.Audio;
    var audio = $audio[0];
    audio.ontimeupdate = function() {
        self.onAudioTimeUpdate(audio);
    };
};

PlayerControl.prototype.onAudioTimeUpdate = function(audio) {
    var normedTime = audio.currentTime / audio.duration * 10000;
    this.DOM.MainSongProgressBar.slider('value', normedTime);
};

PlayerControl.prototype.onProgressSlide = function() {
    //var audio = this.DOM.Audio[0];
    //audio.pause();
    //var normedTime = this.DOM.MainSongProgressBar.slider('value');
    //var time = normedTime / 10000 * audio.duration;
    //audio.currentTime = time;
    //audio.play();
};



PlayerControl.prototype.visualPlay = function($ppButton) {
    if (!$ppButton) {
        $ppButton = this.DOM.MainControlsPlayPause;
    }
    var playPauseClass = rawC(this.C.MainControlsPlayPause);
    $ppButton.removeClass(playPauseClass + '_paused');
    $ppButton.addClass(playPauseClass + '_playing');
    this.setStatePlaying();
};


PlayerControl.prototype.visualPause = function($ppButton) {
    if (!$ppButton) {
        $ppButton = this.DOM.MainControlsPlayPause;
    }
    var playPauseClass = rawC(this.C.MainControlsPlayPause);
    $ppButton.removeClass(playPauseClass + '_playing');
    $ppButton.addClass(playPauseClass + '_paused');
    this.setStatePaused();
};


PlayerControl.prototype.play = function(song_id) {
    var $audio = this.DOM.Audio;
    var audio = $audio[0];
    if (!song_id && !this.playingSongId) {
        this.playlist.playFirst();
    } else if (!song_id) {
        this.visualPlay();
        this.playlist.playingEntry.play();
    }
    if (!song_id || song_id === this.playingSongId) {  // continue playing
        console.log("CONTINUING");
        this.visualPlay();
        //audio.onloadeddata = function() {
        //    audio.play();
        //};
        //audio.load();

    } else {  // new song
        this.visualPlay();
        this.playingSongId = song_id;

        // fetch audio url
    }
};

PlayerControl.prototype.pause = function(stopPlaylist) {
    this.visualPause();
    if (stopPlaylist) {
        this.playlist.pauseCurrent();
    }
    var audio = this.DOM.Audio;
    audio.trigger('pause');
};