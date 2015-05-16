CREATE OR REPLACE VIEW items_features AS
  select app_song.id as song_id,
        CONCAT('[', app_song.id, '] ', SUBSTRING(artist, 1, 30), ' - ', SUBSTRING(title, 1, 30)) as song,
       GROUP_CONCAT(svd_pI.value ORDER by svd_pI.feature_id asc SEPARATOR ', ') as features,
       svd_bI.value as baseline
  from svd_pI
    join app_song on app_song.id = svd_pI.item_id
    left join svd_features on svd_pI.feature_id = svd_features.id
    left join svd_bI on app_song.id = svd_bI.item_id
    GROUP BY app_song.id
    ORDER BY app_song.id
    ;

CREATE OR REPLACE VIEW users_features AS
  select auth_user.id as user_id,
        CONCAT('[', auth_user.id, '] ', auth_user.username) as user,
       GROUP_CONCAT(svd_pU.value ORDER by svd_pU.feature_id asc SEPARATOR ', ') as features,
       svd_bU.value as baseline
    from svd_pU
      join auth_user on auth_user.id = svd_pU.user_id
      left join svd_features on svd_pU.feature_id = svd_features.id
      left join svd_bU on auth_user.id = svd_bU.user_id
      GROUP BY auth_user.id
      ORDER BY auth_user.id
  ;