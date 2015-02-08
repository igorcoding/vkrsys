function Playlist(playlistId, playerControl) {
    this.$obj = $(playlistId);
    this.playerControl = playerControl;
    this.DOM = {};
    this.entries = [];
    this.$entries = null;
    this.playingEntry = null;

    this.bindToDOM();
    this.exploreEntries();
    this.registerEvents();
}

Playlist.prototype.C = {

};

Playlist.prototype.bindToDOM = function() {
    for (var key in this.C) {
        if (this.C.hasOwnProperty(key)) {
            if (key !== 'IGNORED') {
                this.DOM[key] = this.$obj.find(this.C[key]);
            }
        }
    }
};

Playlist.prototype.exploreEntries = function() {
    var self = this;
    this.$entries = this.$obj.find(PlaylistEntry.prototype.C.Entry);
    this.$entries.each(function() {
        self.entries.push(new PlaylistEntry($(this), self));
    });
};

Playlist.prototype.registerEvents = function() {
    window.registerOnResize(this.onWindowResize, this);
    this.onWindowResize(window);
    this.registerEntryHover();
    this.registerPlayPauseHover();
    this.registerEntryPlayPauseClick();
};

Playlist.prototype.onWindowResize = function(w) {
    for (var i = 0; i < this.entries.length; ++i) {
        this.entries[i].onWindowResize(w);
    }
};

Playlist.prototype.registerEntryHover = function() {
    _.forEach(this.entries, function(entry) {
        entry.$obj.hover(function(event) {
            event.stopPropagation();
            entry.onHoverEnter.apply(entry);
        }, function(event) {
            event.stopPropagation();
            entry.onHoverLeave.apply(entry);
        });
    });
};

Playlist.prototype.registerPlayPauseHover = function() {
    _.forEach(this.entries, function(entry) {
        entry.DOM.EntryControlsPlayPause.hover(function(event) {
            event.stopPropagation();
            entry.onPlayPauseHoverEnter.apply(entry);
        }, function(event) {
            event.stopPropagation();
            entry.onPlayPauseHoverEnter.apply(entry);
        });
    });
};

Playlist.prototype.registerEntryPlayPauseClick = function() {
    var self = this;
    var playPauseClickCb = function(entry, isHoveringPlayPause, isHoveringEntry) {
        var state = entry.getState();
        console.log(state);

        var song_id = entry.getSongId();
        if (song_id) {
            switch (state) {
                case PlaylistEntry.prototype.States.Playing:
                    entry.visualPause(isHoveringPlayPause, isHoveringEntry);
                    self.playingEntry = null;

                    self.playerControl.pause();
                    break;
                case PlaylistEntry.prototype.States.Paused:
                default:
                    if (self.playingEntry) {
                        self.playingEntry.visualPause();
                    }
                    entry.visualPlay();
                    self.playingEntry = entry;

                    self.playerControl.pause();
                    self.playerControl.play(song_id);
                    break;
            }
        }
        console.log(entry.getState());
    };

    _.forEach(this.entries, function(entry) {
        entry.DOM.EntryControlsPlayPause.click(function(event) {
            event.stopPropagation();
            playPauseClickCb(entry, false, true);
        });

        entry.DOM.Entry.click(function() {
            playPauseClickCb(entry, false, true);
        })
    });
};