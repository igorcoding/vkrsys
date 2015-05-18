define(['PlayerApp/PlayerControl', 'PlayerApp/Playlist', 'UsersCards'],
    function(PlayerControl, Playlist, UsersCards) {
        function Player(playerId, playlistId, usersCardsId, contentLoader) {
            this.playlist = new Playlist(playlistId);
            this.usersCards = new UsersCards(usersCardsId);
            this.playerControl = new PlayerControl(playerId, this.playlist, this.usersCards, contentLoader, {
                playpause: 'p',
                prev: 'b',
                next: 'n',
                like: 'l',
                dislike: 'd',
                refresh: 'r',
                toggle: 't'
            });
            this.usersCards.setPlayerControl(this.playerControl);
            this.playlist.setPlayerControl(this.playerControl);

            this.usersCards.loadCards();
        }

        return Player;
    }
);