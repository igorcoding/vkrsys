define(['jquery', 'PlaylistEntry'],
    function($, PlaylistEntry) {
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

        Playlist.prototype = {
            C: {},

            bindToDOM: function () {
                for (var key in this.C) {
                    if (this.C.hasOwnProperty(key)) {
                        if (key !== 'IGNORED') {
                            this.DOM[key] = this.$obj.find(this.C[key]);
                        }
                    }
                }
            },

            exploreEntries: function (count) {
                var self = this;
                this.$entries = this.$obj.find(PlaylistEntry.prototype.C.Entry);
                if (count && this.entries.length > 0) {
                    this.$entries = this.$entries.slice(this.entries.length, this.entries.length + count);
                }
                //this.entries = [];
                var id = -1;
                this.$entries.each(function () {
                    var $this = $(this);
                    var entry = new PlaylistEntry($this, self);
                    ++id;
                    self.entries.push(entry);
                    self.registerThings($this, entry, id);
                });
            },

            registerEvents: function () {
                //window.registerOnResize(this.onWindowResize, this);
                //this.onWindowResize(window);
            },

            onWindowResize: function (w) {
                PlaylistEntry.prototype.onWindowResize(w, this.$obj.find(PlaylistEntry.prototype.C.EntryInfo));
            },

            registerThings: function ($entry, entry, id) {
                var self = this;
                var playPauseClickCb = function (entry, id) {
                    var state = entry.getState();
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
                                self.playingEntryId = id;

                                self.playerControl.play(entry);
                                break;
                        }
                    }
                    console.log('[Playlist] song = ' + entry.getSongId() + '; new state = ' + entry.getState());
                };

                //for (var id = 0; id < this.entries.length; ++id) {}
                //_.forEach(this.entries, function(entry, id) {
                entry.DOM.EntryControlsPlayPause.click(function (event) {
                    event.stopPropagation();
                    playPauseClickCb(entry, id);
                });

                entry.DOM.Entry.click(function () {
                    playPauseClickCb(entry, id);
                });

                entry.DOM.EntryControlsLikeJs.click(function (event) {
                    event.stopPropagation();
                    entry.like();
                });

                entry.DOM.EntryControlsDislikeJs.click(function (event) {
                    event.stopPropagation();
                    entry.dislike();
                });

                entry.DOM.Entry.hover(entry.onHoverEnter.bind(entry),
                    entry.onHoverLeave.bind(entry));
                //});

                //entry.onWindowResize(window);
            },

            playById: function (id) {
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
            },

            playFirst: function () {
                this.playById(0);
            },

            pauseCurrent: function () {
                this.playingEntry.pause();
            },

            next: function () {
                this.playById(this.playingEntryId + 1);
            },

            prev: function () {
                this.playById(this.playingEntryId - 1);
            }
        };

        return Playlist;
    }
);
