from flask_marshmallow import Marshmallow
from models import Artist, Album, Track

ma = Marshmallow()


class ArtistSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Artist
        load_instance = True
        fields = ("id", "name", "age", "albums", "tracks", "self")

class AlbumSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Album
        load_instance = True
        fields = ("id", "artist_id", "name", "genre", "artist", "tracks", "self")

class TrackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Track
        load_instance = True
        fields = ("id", "album_id", "name", "duration", "times_played", "artist", "album", "self")

artist_schema = ArtistSchema()
artists_schema = ArtistSchema(many=True)

album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)

track_schema = TrackSchema()
tracks_schema = TrackSchema(many=True)