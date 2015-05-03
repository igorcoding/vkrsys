define(['jquery'],
    function($) {
        function PlayerProgressbar($obj, sliderMax) {
            this.$obj = $obj;
            if (!this.$obj) {
                throw "obj must be defined";
            }
            this.width = this.$obj.width();
            this.height = this.$obj.height();
            this.DOM = {};
            this.bindToDOM();
            this.registerEvents();

            this.progressManualSliding = false;
            this.afterManualSlide = false;
            this.sliderMax = sliderMax;
            this.prevAudioTime = -1;

            this.currentProgress = 0;
            this.manualSlideCallbacks = [];
            this._dragging = false;
        }

        PlayerProgressbar.prototype = {
            C: {
                Bg: '.player__progressbar__bg',
                Progress: '.player__progressbar__progress'
            },

            bindToDOM: function () {
                for (var key in this.C) {
                    if (this.C.hasOwnProperty(key)) {
                        if (key !== 'IGNORED') {
                            this.DOM[key] = this.$obj.find(this.C[key]);
                        }
                    }
                }
            },

            registerEvents: function() {
                var self = this;

                var onMouseCb = function(e) {
                    var posX = self.$obj.offset().left,
                        posY = self.$obj.offset().top;
                    var px = e.pageX - posX;
                    var progress = self._pxToProgress(px);
                    self._changeProgress(progress);
                    return progress;
                };

                this.$obj
                    .mousedown(function(e) {
                        self._dragging = true;
                        $(window).mousemove(function (e) {
                            if (self._dragging) {
                                onMouseCb(e);
                            }
                        });
                        $(window).mouseup(function(e) {
                            if (self._dragging) {
                                self._dragging = false;
                                $(window).off("mouseup");
                            }
                        });
                    })
                    .mouseup(function(e) {
                        $(window).off("mousemove");
                        self._dragging = false;
                        var progress = onMouseCb(e);

                        for (var i = 0; i < self.manualSlideCallbacks.length; ++i) {
                            self.manualSlideCallbacks[i](progress);
                        }
                    });
            },


            isChangingManually: function() {
                return this._dragging;
            },

            addOnProgressChangedManuallyListener: function(cb) {
                this.manualSlideCallbacks.push(cb);
            },

            changeProgress: function(progress) {
                this._changeProgress(progress);
            },

            resetProgress: function() {
                this._changeProgress(0);
            },

            _changeProgress: function(progress) {
                this.currentProgress = progress;
                var px = this._progressToPx(this.currentProgress);
                this.DOM.Progress.css('clip', 'rect(0px ' + px + 'px ' + this.height + 'px 0px)');
            },

            _progressToPx: function(progress) {
                return progress * this.width / this.sliderMax;
            },

            _pxToProgress: function(px) {
                return px * this.sliderMax / this.width;
            }
        };

        return PlayerProgressbar;
    }
);