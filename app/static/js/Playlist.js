function Playlist(playlistId, playerControl) {
    this.$obj = $(playlistId);
    this.playerControl = playerControl;
    this.DOM = {};
    this.entries = [];
    this.$entries = null;
    this.playingEntry = null;
    this.playingEntryId = null;

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
    this.registerEntryControlsClick();
};

Playlist.prototype.onWindowResize = function(w) {
    for (var i = 0; i < this.entries.length; ++i) {
        this.entries[i].onWindowResize(w);
    }
};

Playlist.prototype.registerEntryControlsClick = function() {
    var self = this;
    var playPauseClickCb = function(entry, id) {
        var state = entry.getState();
        console.log(state);

        var song_id = entry.getSongId();
        if (song_id) {
            switch (state) {
                case PlaylistEntry.prototype.States.Playing:
                    entry.visualPause();

                    self.playerControl.pause();
                    break;
                case PlaylistEntry.prototype.States.Paused:
                default:
                    if (self.playingEntry) {
                        self.playingEntry.visualPause();
                    }
                    entry.visualPlay();
                    self.playingEntry = entry;
                    this.playingEntryId = id;

                    self.playerControl.play(entry);
                    break;
            }
        }
        console.log(entry.getState());
    };

    _.forEach(this.entries, function(entry, id) {
        entry.DOM.EntryControlsPlayPause.click(function(event) {
            event.stopPropagation();
            playPauseClickCb(entry, id);
        });

        entry.DOM.Entry.click(function() {
            playPauseClickCb(entry, id);
        });

        entry.DOM.EntryControlsLike.click(function(event) {
            event.stopPropagation();
            entry.like();
        });

        entry.DOM.EntryControlsDislike.click(function(event) {
            event.stopPropagation();
            entry.dislike();
        });
    });
};

Playlist.prototype.playById = function(id) {
    if (id < 0) {
        id = this.entries.length - 1;
    }
    if (id >= this.entries.length) {
        id = 0;
    }
    if (this.playingEntry) {
        this.playingEntry.pause();
    }
    this.playingEntryId = id;
    this.playingEntry = this.entries[id];
    this.playingEntry.play();
    this.playerControl.play(this.playingEntry);
};

Playlist.prototype.playFirst = function() {
    this.playById(0);
};

Playlist.prototype.pauseCurrent = function() {
    this.playingEntry.pause();
};

Playlist.prototype.next = function() {
    this.playById(this.playingEntryId + 1);
};

Playlist.prototype.prev = function() {
    this.playById(this.playingEntryId - 1);
};