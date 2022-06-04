select ar.artist_name,
       ar.artist_popularity,
       ar.followers,
       ar.monthly_listeners,
       tf.danceability,
       tf.loudness,
       tf.energy,
       tf.key,
       tf.`mode`,
       tf.speechiness,
       tf.acousticness,
       tf.instrumentalness,
       tf.liveness,
       tf.valence,
       tf.tempo,
       tf.duration_ms,
       tf.time_signature,
       t.track_popularity,
       t.track_name,
       alb.release_date
from artists as ar
         INNER JOIN tracks_artists AS ta ON ta.artist_id = ar.id
         INNER JOIN track_features AS tf ON tf.track_id = ta.track_id
         INNER JOIN tracks AS t ON t.id = ta.track_id
         INNER JOIN albums_tracks AS al_tr ON al_tr.track_id = t.id
         INNER JOIN albums AS alb ON alb.id = al_tr.album_id
ORDER BY alb.release_date DESC;