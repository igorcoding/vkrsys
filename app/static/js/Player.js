define(['PlayerControl', 'Playlist'],
    function(PlayerControl, Playlist) {
        function Player(playerId, playlistId) {
            this.playerControl = new PlayerControl(playerId);
            this.playlist = new Playlist(playlistId, this.playerControl);
            this.playerControl.setPlaylist(this.playlist);
        }

        return Player;
    }
);