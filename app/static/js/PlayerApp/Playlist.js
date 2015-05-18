define(['jquery', 'PlayerApp/PlaylistEntry'],
    function($, PlaylistEntry) {
        function Playlist(playlistId) {
            this.$obj = $(playlistId);
            this.$objp = this.$obj.parent();
            this.playerControl = null;
            this.DOM = {};
            this.entries = [];
            this.$entries = null;
            this.playingEntry = null;
            this.playingEntryId = null;

            this.onScrollListeners = [];

            this.ITEMS_SCROLL_ANIMATION_SPEED = 600;


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

            show: function() {
                this.$objp.show();
                //this.scrollToCurrent();
            },

            hide: function() {
                this.$objp.hide();
            },

            isVisible: function() {
                return this.$obj.is(':visible');
            },

            setPlayerControl: function (playerControl) {
                this.playerControl = playerControl;
            },

            addContent: function(content) {
                this.$obj.append(content.result);
                this.exploreEntries(content.count);
            },

            replaceContent: function(content) {
                this.$obj.empty();
                this.entries = [];
                this.$obj.append(content.result);
                this.exploreEntries(content.count);
            },

            exploreEntries: function (count) {
                var self = this;
                var $allEntries = this.$obj.find(PlaylistEntry.prototype.C.Entry);
                var $entries;
                if (count && this.entries.length > 0) {
                    $entries = $allEntries.slice(this.entries.length, this.entries.length + count);
                } else {
                    $entries = $allEntries;
                }
                //this.entries = [];
                var id = this.entries.length - 1;
                $entries.each(function () {
                    var $this = $(this);
                    var entry = new PlaylistEntry($this, self);
                    ++id;
                    self.entries.push(entry);
                    self.registerThings($this, entry, id);
                });
                this.$entries = $allEntries;
            },

            registerEvents: function () {
                var self = this;
                this.$objp.scroll(function() {
                    for (var i = 0; i < self.onScrollListeners.length; ++i) {
                        self.onScrollListeners[i](self.$objp);
                    }
                });
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

            addOnScrollListener: function(cb) {
                this.onScrollListeners.push(cb);
            },

            setPlaying: function(id) {
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
                return this.playingEntry;
            },

            playById: function (id, forcePlay) {
                //console.log("Entries length:", this.entries.length);
                //console.log("PlayingId:", this.playingEntryId);
                this.setPlaying(id);
                this.playingEntry.play();
                this.playerControl.play(this.playingEntry, forcePlay);
            },

            playFirst: function () {
                this.playById(0, true);
            },

            pauseCurrent: function () {
                this.playingEntry.pause();
            },

            next: function () {
                this.playById(this.playingEntryId + 1);
            },

            prev: function () {
                this.playById(this.playingEntryId - 1);
            },

            scrollToCurrent: function() {
                var scrollTo = this.playingEntryId;
                this.scrollTo(scrollTo);
            },

            scrollTo: function(id) {
                console.log(id);
                var extraPadding = 10;
                if (id != null && typeof id != 'undefined' && id < this.$entries.length) {
                    this.$objp.animate({
                        scrollTop: this.$objp.scrollTop()
                        + $(this.$entries[id]).offset().top
                        - this.$objp.offset().top - extraPadding
                    }, this.ITEMS_SCROLL_ANIMATION_SPEED);
                }
            }

        };

        return Playlist;
    }
);
