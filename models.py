from flask import url_for
from flask_sqlalchemy import SQLAlchemy

nombre_ruta = "127.0.0.1:5000/"

db = SQLAlchemy()


#string = "Michael Jackson"
#encoded = b64encode(string.encode()).decode('utf-8') 
#print(encoded)


#class Artist(db.Model): []
#    id = db.Column(db.Integer, primary_key=True)
#    slug = db.Column(db.String(64), index=True)
#    name = db.Column(db.String(64), nullable=False)
#    image_url = db.Column(db.String(128), nullable=False)

#    @property
#    def url(self):
#        return url_for("get_artist", id=self.id)

class Artist(db.Model):
    id = db.Column(db.String(64), primary_key = True)
    name = db.Column(db.String(64), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    
    #albums = db.relationship('Albums', backref='artist', lazy=True)
    #tracks = db.relationship('Tracks', backref='album', lazy=True) #VER LO DE LAZY
    albums = db.Column(db.String(64), nullable = True)
    tracks = db.Column(db.String(64), nullable = True)
    self = db.Column(db.String(64), nullable = True)
    
    @property
    def self(self):
        return url_for("get_artist", id=self.id)

    @property
    def albums(self):
        album = self.self + "/albums"
        return album

    @property
    def tracks(self):
        track = self.self + "/tracks"
        return track

class Album(db.Model):
    id = db.Column(db.String(64), primary_key = True)
    name = db.Column(db.String(64), nullable = False) 
    genre = db.Column(db.String(64), nullable = False)
    artist_id = db.Column(db.String(64), nullable=False)
    
    #tracks = db.relationship('Tracks', backref='album', lazy=True) #VER LO DE LAZY
    artist = db.Column(db.String(64), nullable = True)
    tracks = db.Column(db.String(64), nullable = True)
    self = db.Column(db.String(64), nullable = True)
    
    @property
    def self(self):
        return url_for("get_album", id=self.id)

    @property
    def artist(self):
        album = nombre_ruta + self.artist_id
        return album

    @property
    def tracks(self):
        track = self.self + "/tracks"
        return track


class Track(db.Model):
    id = db.Column(db.String(64), primary_key = True)
    name = db.Column(db.String(64), nullable = False)
    duration = db.Column(db.Float, nullable = False)
    times_played = db.Column(db.Integer, nullable = False)
    album_id = db.Column(db.String(64), nullable=False)
    
    artist = db.Column(db.String(64), nullable = True)
    album = db.Column(db.String(64), nullable = True)
    self = db.Column(db.String(64), nullable = True)
    
    @property
    def artist(self):
        album = Album.query.get_or_404(self.album_id)
        id_artista = album.artist_id
        return url_for("get_artist", id=id_artista)

    @property
    def album(self):
        return url_for("get_album", id=self.album_id)
    
    @property
    def self(self):
        return url_for("get_track", id=self.id)
