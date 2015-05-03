define(['PlayerControl', 'Playlist'],
    function(PlayerControl, Playlist) {
        function Player(playerId, playlistId) {
            this.playerControl = new PlayerControl(playerId);
        }

        return Player;
    }
);