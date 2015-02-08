function PlayerControl(playerId) {
    this.$obj = $(playerId);
    this.DOM = {};
    this.bindToDOM();
    this.registerEvents();

    this.playingSongId = null;
    this.state = 'paused';
}

PlayerControl.prototype.States = {
    Paused: 'paused',
    Playing: 'playing'
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
};

PlayerControl.prototype.registerEvents = function() {
    window.registerOnResize(this.onWindowResize, this);
    this.onWindowResize(window);
};

PlayerControl.prototype.onWindowResize = function(w) {

};






PlayerControl.prototype.play = function(song_id) {
    // fetch audio url

    this.playingSongId = song_id;
};

PlayerControl.prototype.pause = function() {

};