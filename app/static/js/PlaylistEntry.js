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
}

PlaylistEntry.prototype.States = {
    Paused: 'paused',
    Playing: 'playing'
};

PlaylistEntry.prototype.getState = function() {
    return this.state || this.States.Paused;
};

PlaylistEntry.prototype._setState = function(state) {
    this.state = state;
};

PlaylistEntry.prototype.setStatePaused = function() {
    this._setState(this.States.Paused);
};

PlaylistEntry.prototype.setStatePlaying = function() {
    this._setState(this.States.Playing);
};

PlaylistEntry.prototype.getSongId = function() {
    return this.$obj.data('song_id') || null;
};

PlaylistEntry.prototype.C = {
    Entry: '.playlist__entry',
    EntryInfo: '.playlist__entry__info',
    EntryArt: '.playlist__entry__art',
    EntryHeader: '.playlist__entry__header',
    EntryHeaderArtist: '.playlist__entry__title__artist',
    EntryHeaderTitle: '.playlist__entry__title__title',
    EntryControlsPlayPause: '.playlist__entry__controls__playpause'
};

PlaylistEntry.prototype.bindToDOM = function() {
    for (var key in this.C) {
        if (this.C.hasOwnProperty(key)) {
            if (key !== 'IGNORED') {
                this.DOM[key] = this.$obj.find(this.C[key]);
            }
        }
    }
};

PlaylistEntry.prototype.onWindowResize = function(w) {
    var entryInfo = this.DOM.EntryInfo;
    var entryArt = this.DOM.EntryArt;
    var entryHeader = this.DOM.EntryHeader;
    var entryHeaderMargin = entryHeader.margin();
    var playPause = entryInfo.find(this.C.EntryControlsPlayPause);

    entryInfo.width(entryInfo.parent().width());

    var minus = entryInfo.width() - entryArt.totalWidth()
                                       - entryHeaderMargin.left
                                       - entryHeaderMargin.right
                                       - playPause.totalWidth() - 1;
    entryHeader.width(minus);
};

PlaylistEntry.prototype.onHoverEnter = function() {
    var art = this.$obj.find(this.C.EntryArt);
    var playPause = this.$obj.find(this.C.EntryControlsPlayPause);

    var state = this.getState();
    if (state !== this.States.Playing) {
        this.$obj.addClass('playlist__entry_hover');
    }
    this.onPlayPauseHoverEnter(playPause);
    //art.addClass(dimmedClassName);
    //playPause.show();
};

PlaylistEntry.prototype.onHoverLeave = function() {
    var art = this.$obj.find(this.C.EntryArt);
    var playPause = this.$obj.find(this.C.EntryControlsPlayPause);

    this.$obj.removeClass('playlist__entry_hover');

    this.onPlayPauseHoverLeave(playPause);
    //art.removeClass(dimmedClassName);
    //playPause.hide();
};

PlaylistEntry.prototype.onPlayPauseHoverEnter = function() {
    var state = this.getState();
    switch (state) {
        case this.States.Playing:
            this.DOM.EntryControlsPlayPause.addClass('playlist__entry__controls__playpause_playing_hover');
            break;
        case this.States.Paused:
        default:
            this.DOM.EntryControlsPlayPause.addClass('playlist__entry__controls__playpause_paused_hover');
            break;
    }
};

PlaylistEntry.prototype.onPlayPauseHoverLeave = function() {
    this.DOM.EntryControlsPlayPause.removeClass('playlist__entry__controls__playpause_playing_hover');
    this.DOM.EntryControlsPlayPause.removeClass('playlist__entry__controls__playpause_paused_hover');
};

PlaylistEntry.prototype.visualPause = function(isHoveringPlayPause, isHoveringEntry) {
    var $playPause = this.DOM.EntryControlsPlayPause;
    $playPause.removeClass('playlist__entry__controls__playpause_playing');
    $playPause.removeClass('playlist__entry__controls__playpause_playing_hover');
    $playPause.addClass('playlist__entry__controls__playpause_paused');


    this.$obj.removeClass('playlist__entry_playing');
    if (isHoveringPlayPause) {
        $playPause.addClass('playlist__entry__controls__playpause_paused_hover');
    }
    if (isHoveringEntry) {
        this.$obj.addClass('playlist__entry_hover');
    }

    this.setStatePaused();
};

PlaylistEntry.prototype.visualPlay = function() {
    var $playPause = this.DOM.EntryControlsPlayPause;
    $playPause.removeClass('playlist__entry__controls__playpause_paused');
    $playPause.removeClass('playlist__entry__controls__playpause_paused_hover');
    $playPause.addClass('playlist__entry__controls__playpause_playing');
    $playPause.addClass('playlist__entry__controls__playpause_playing_hover');
    this.$obj.removeClass('playlist__entry_hover');
    this.$obj.addClass('playlist__entry_playing');

    this.setStatePlaying();
};