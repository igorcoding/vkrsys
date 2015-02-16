function ContentLoader() {
    this.$obj = $(document);
    this.DOM = {};
    this.bindToDOM();
    this.limit = 30;
    this.offset = 0;
}

ContentLoader.prototype.C = {
    UserAvatar: '.main-header__toolbar__user__avatar',
    MainContentInner: '.main-content__inner',
    PlaylistContents: '.playlist'
};

ContentLoader.prototype.bindToDOM = function() {
    for (var key in this.C) {
        if (this.C.hasOwnProperty(key)) {
            if (key !== 'IGNORED') {
                this.DOM[key] = this.$obj.find(this.C[key]);
            }
        }
    }
};

ContentLoader.prototype.fetchUserpic = function() {
    var self = this;
    $.ajax('/api/userpic', {
        method: 'GET'
    })
        .done(function(d) {
            console.log(d);
            if (d.status === 200) {
                self.DOM.UserAvatar.css('background-image', 'url(' + d.url + ')')
            } else if (d.status !== 501) {
                setTimeout(function() {
                    console.log('[userpic] Retrying to fetch userpic');
                    self.fetchUserpic();
                }, 5000);
            }
        })
        .fail(function(d) {
            console.warn('[userpic] disaster: ', d);
        });
};

ContentLoader.prototype.loadInitialRecommendations = function(cb) {
    var self = this;
    cb = cb || function() {};

    this.offset = 0;
    this.loadRecommendations(this.limit, this.offset, true, function(d) {
        self.DOM.MainContentInner.html(d.result);
        self.bindToDOM();
        cb();
    });
};

ContentLoader.prototype.loadNextRecommendations = function(cb) {
    var self = this;
    cb = cb || function() {};

    this.loadRecommendations(this.limit, this.offset, false, function(d) {
        console.log(d);
        console.log(self.DOM.PlaylistContents);
        self.DOM.PlaylistContents.append(d.result);
        window.player.playlist.exploreEntries();
        cb();
    });
};

ContentLoader.prototype.loadRecommendations = function(limit, offset, initial, cb) {
    var self = this;
    cb = cb || function() {};

    var retrial = function(timeout) {
        setTimeout(function() {
            console.log('[recommend] Retrying to fetch recommendations');
            self.loadInitialRecommendations();
        }, timeout);
    };

    $.ajax('/api/recommend', {
        method: 'GET',
        data: {
            limit: limit,
            offset: offset,
            initial: initial ? 1 : 0
        }
    })
        .done(function(d) {
            if (d.status == 200) {
                self.offset += self.limit;
                cb(d);
            } else {
                retrial(500);
            }
        })
        .fail(function(d) {
            console.warn('[recommend] disaster: ', d);
            retrial(2000);
        });
};