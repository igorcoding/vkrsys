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
    EntryControlsPlayPause: '.playlist__entry__controls__playpause',
    EntryControls: '.playlist__entry__controls',
    EntryControlsLike: '.playlist__entry__controls__like',
    EntryControlsDislike: '.playlist__entry__controls__dislike'
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
    this.DOM.EntryControls.show();
};

PlaylistEntry.prototype.onHoverLeave = function() {
    this.DOM.EntryControls.hide();
};

PlaylistEntry.prototype.visualPause = function() {
    var $playPause = this.DOM.EntryControlsPlayPause;
    var ppClass = rawC(this.C.EntryControlsPlayPause);
    var entryClass = rawC(this.C.Entry);
    $playPause.removeClass(ppClass + '_playing');
    $playPause.addClass(ppClass + '_paused');

    this.$obj.removeClass(entryClass + '_playing');
    this.$obj.addClass(entryClass + '_paused');

    this.setStatePaused();
};

PlaylistEntry.prototype.visualPlay = function() {
    var $playPause = this.DOM.EntryControlsPlayPause;
    var ppClass = rawC(this.C.EntryControlsPlayPause);
    var entryClass = rawC(this.C.Entry);
    $playPause.removeClass(ppClass + '_paused');
    $playPause.addClass(ppClass + '_playing');
    this.$obj.removeClass(entryClass + '_hover');
    this.$obj.addClass(entryClass + '_playing');

    this.setStatePlaying();
};

PlaylistEntry.prototype.play = function() {
    this.visualPlay();
};

PlaylistEntry.prototype.pause = function() {
    this.visualPause();
};

PlaylistEntry.prototype.rate = function(direction) {
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
        .done(function(data) {
            console.log(data);
        })
        .fail(function(data) {
            console.warn(data);
        });
};

PlaylistEntry.prototype.like = function() {
    this.rate('up');
};

PlaylistEntry.prototype.dislike = function() {
    this.rate('down');
};