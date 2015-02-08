function Player(playerId, playlistId) {
    this.$player = $(playerId);
    this.$playlist = $(playlistId);
    this.bindToDOM();
    this.registerEvents();
}

Player.prototype.C = {
    Player: {
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
    Playlist: {
        Entry: '.playlist__entry',
        EntryInfo: '.playlist__entry__info',
        EntryArt: '.playlist__entry__art',
        EntryHeader: '.playlist__entry__header',
        EntryHeaderArtist: '.playlist__entry__title__artist',
        EntryHeaderTitle: '.playlist__entry__title__title'
    }
};

Player.prototype.registerEvents = function() {
    window.registerOnResize(this.onWindowResize, this);
    this.onWindowResize(window);
    this.registerPlaylistEntryHover();
    this.registerPlaylistPlayPauseHover();
    this.registerPlaylistEntryPlayClick();
};

Player.prototype.bindToDOM = function() {
    this.DOM = {};

    for (var entity in this.C) {
        if (this.C.hasOwnProperty(entity)) {
            var e = this.C[entity];
            this.DOM[entity] = {};
            for (var key in e) {
                if (e.hasOwnProperty(key)) {
                    var parent = $(document);
                    if (entity.toLowerCase() === 'player') {
                        parent = this.$player;
                    } else if (entity.toLowerCase() === 'playlist') {
                        parent = this.$playlist;
                    }
                    this.DOM[entity][key] = parent.find(e[key]);
                }
            }
        }
    }
};

Player.prototype.onWindowResize = function(w) {
    var entryInfo = this.DOM.Playlist.EntryInfo;
    var entryArt = this.DOM.Playlist.EntryArt;
    var entryHeader = this.DOM.Playlist.EntryHeader;
    var entryHeaderMargin = entryHeader.margin();
    var playPause = entryInfo.find(".playlist__entry__controls__playpause");

    entryInfo.width(entryInfo.parent().width());

    var minus = entryInfo.width() - entryArt.totalWidth()
                                       - entryHeaderMargin.left
                                       - entryHeaderMargin.right
                                       - playPause.totalWidth() - 1;
    entryHeader.width(minus);
};

Player.prototype.registerPlaylistEntryHover = function() {
    var self = this;
    var dimmedClassName = 'playlist__entry__art_dimmed';
    this.DOM.Playlist.Entry.hover(function() {
        var $this = $(this);
        var art = $this.find(self.C.Playlist.EntryArt);
        var playPause = $this.find(".playlist__entry__controls__playpause");

        var state = $this.data("state") || "paused";
        if (state !== "playing") {
            $this.addClass('playlist__entry_hover');
        }
        //art.addClass(dimmedClassName);
        //playPause.show();
    }, function() {
        var $this = $(this);
        var art = $this.find(self.C.Playlist.EntryArt);
        var playPause = $this.find(".playlist__entry__controls__playpause");

        $this.removeClass('playlist__entry_hover');
        //art.removeClass(dimmedClassName);
        //playPause.hide();
    });
};

Player.prototype.registerPlaylistPlayPauseHover = function() {
    var self = this;
    this.DOM.Playlist.Entry.find(".playlist__entry__controls__playpause").hover(function() {
        var $this = $(this);
        var entry = $this.closest(self.C.Playlist.Entry);
        var state = entry.data("state");
        switch (state) {
            case "playing":
                $this.addClass('playlist__entry__controls__playpause_playing_hover');
                break;
            case "paused":
            default:
                $this.addClass('playlist__entry__controls__playpause_paused_hover');
                break;
        }
    }, function() {
        var $this = $(this);
        var entry = $this.closest(self.C.Playlist.Entry);
        var state = entry.data("state");

        $this.removeClass('playlist__entry__controls__playpause_playing_hover');
        $this.removeClass('playlist__entry__controls__playpause_paused_hover');
    });
};

Player.prototype.prePause = function($entry, isHoveringPlayPause, isHoveringEntry) {
    var $playPause = $entry.find('.playlist__entry__controls__playpause');
    $playPause.removeClass('playlist__entry__controls__playpause_playing');
    $playPause.removeClass('playlist__entry__controls__playpause_playing_hover');
    $playPause.addClass('playlist__entry__controls__playpause_paused');

    $entry.data("state", "paused");
    $entry.removeClass('playlist__entry_playing');
    if (isHoveringPlayPause) {
        $playPause.addClass('playlist__entry__controls__playpause_paused_hover');
    }
    if (isHoveringEntry) {
        $entry.addClass('playlist__entry_hover');
    }
};

Player.prototype.prePlay = function($entry) {
    var $playPause = $entry.find('.playlist__entry__controls__playpause');
    $playPause.removeClass('playlist__entry__controls__playpause_paused');
    $playPause.removeClass('playlist__entry__controls__playpause_paused_hover');
    $playPause.addClass('playlist__entry__controls__playpause_playing');
    $playPause.addClass('playlist__entry__controls__playpause_playing_hover');
    $entry.data("state", "playing");
    $entry.removeClass('playlist__entry_hover');
    $entry.addClass('playlist__entry_playing');
};

Player.prototype.registerPlaylistEntryPlayClick = function() {
    var self = this;
    var playPauseClickCb = function(entry, isHoveringPlayPause, isHoveringEntry) {
        var state = entry.data("state") || "paused";

        var song_id = entry.data("song_id") || null;
        switch (state) {
            case "playing":
                self.prePause(entry, isHoveringPlayPause, isHoveringEntry);

                if (song_id) {
                    self.pause(song_id);
                }
                break;
            case "paused":
            default:
                self.DOM.Playlist.Entry.each(function() {
                    self.prePause($(this));
                });

                self.prePlay(entry);

                if (song_id) {
                    self.pause();
                    self.play(song_id);
                }
                break;
        }
    };

    this.DOM.Playlist.Entry.find('.playlist__entry__controls__playpause').click(function() {
        var $this = $(this);
        var entry = $this.closest(self.C.Playlist.Entry);
        playPauseClickCb(entry, true, true);
    });

    this.DOM.Playlist.Entry.click(function() {
        playPauseClickCb($(this), false, true);
    });
};

Player.prototype.play = function(song_id) {
    // fetch audio url
};

Player.prototype.pause = function(song_id) {

};