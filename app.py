import sys
from flask import Flask, jsonify, request
from marshmallow.exceptions import ValidationError
from models import db, Artist, Album, Track
from schemas import ma, artist_schema, artists_schema, album_schema, albums_schema, track_schema, tracks_schema
from slugify import slugify
from base64 import b64encode
from decouple import config as config_decouple


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///artist.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
ma.init_app(app)

def base64(string):
    encoded = b64encode(string.encode()).decode('utf-8')
    return str(encoded)


#------------ GET ------------#


#------ GET ARTISTAS, ALBUMS Y CANCIONES POR ID ------#

@app.route("/artists/<id>", methods=["GET"])
def get_artist(id):
    artist = Artist.query.get_or_404(id)
    return artist_schema.jsonify(artist)

@app.route("/albums/<id>", methods=["GET"])
def get_album(id):
    album = Album.query.get_or_404(id)
    return album_schema.jsonify(album)

@app.route("/tracks/<id>", methods=["GET"])
def get_track(id):
    track = Track.query.get_or_404(id)
    return track_schema.jsonify(track)


#------ OBTIENE TODOS LOS ARTISTAS, ALBUMS Y CANCIONES ------#

@app.route("/artists/", methods=["GET"])
def list_artists():
    all_artists = Artist.query.all()
    return artists_schema.jsonify(all_artists)

@app.route("/albums/", methods=["GET"])
def list_albums():
    all_albums = Album.query.all()
    return albums_schema.jsonify(all_albums)

@app.route("/tracks/", methods=["GET"])
def list_tracks():
    all_tracks = Track.query.all()
    return tracks_schema.jsonify(all_tracks)


#-------- Obtener los albums por artista --------#

@app.route("/artist/<id>/albums", methods=["GET"])
def list_albums_per_artist(id):
    artist = Artist.query.get_or_404(id)
    all_albums = Album.query.filter(Album.artist_id == id)
    return albums_schema.jsonify(all_albums)

#-------- Obtener las canciones por artista --------#

@app.route("/artist/<id>/tracks", methods=["GET"])
def list_tracks_per_artist(id):
    artist = Artist.query.get_or_404(id)
    album_artista = Album.query.filter(Album.artist_id == id).all()
    
    lista_album = []
    all_tracks = []

    for album in album_artista:
        if album.id not in lista_album:
            lista_album.append(album.id)

    for album_id in lista_album:
        tracks_album = Track.query.filter(Track.album_id == album_id).all()
        all_tracks.append(tracks_album[0])
    

    return tracks_schema.jsonify(all_tracks)

#-------- Obtener todas las canciones por album --------#

@app.route("/album/<id>/tracks", methods=["GET"])
def list_tracks_per_album(id):
    album = Album.query.get_or_404(id)
    all_tracks = Track.query.filter(Track.album_id == id)
    return tracks_schema.jsonify(all_tracks)

# ---------------- POST ----------------#


# -------- CREAR ARTISTAS, ALBUMS Y CANCIONES --------#

@app.route("/artists/", methods=["POST"])
def create_artist():
    
    try:
        request.json["id"] = base64(request.json["name"])[:22]
        artist = artist_schema.load(request.json, session=db.session)
    
    except ValidationError as errors:
        resp = jsonify(errors.messages)
        resp.status_code = 400
        return resp

    db.session.add(artist)
    db.session.commit()

    resp = jsonify({"message": "created"})
    resp.status_code = 201
    resp.headers["Location"] = artist.self 
    return resp


@app.route("/artists/<id>/albums", methods=["POST"]) 
def create_albums(id):
    try:
        request.json["artist_id"] = id
        album_id = base64(request.json["name"] + ":" + id)[:22]
        request.json["id"] = album_id
        print(request.json)
        album = album_schema.load(request.json, session=db.session)

    except ValidationError as errors:
        resp = jsonify(errors.messages)
        resp.status_code = 400
        return resp

    db.session.add(album)
    db.session.commit()

    resp = jsonify({"message": "created"})
    resp.status_code = 201
    resp.headers["Location"] = album.self 
    return resp


@app.route("/albums/<id>/tracks", methods=["POST"]) 
def create_track(id):
    try:
        track_id = base64(request.json["name"] + ":" + id)[:22]
        request.json["id"] = track_id
        request.json["album_id"] = id
        request.json["times_played"] = 0
        track = track_schema.load(request.json, session=db.session)

    except ValidationError as errors:
        resp = jsonify(errors.messages)
        resp.status_code = 400
        return resp

    db.session.add(track)
    db.session.commit()

    resp = jsonify({"message": "created"})
    resp.status_code = 201
    resp.headers["Location"] = track.self 
    return resp


#------------ PUT ------------#
@app.route("/artists/<artist_id>/albums/play", methods=["PUT"])
def play_artist_tracks(artist_id):
    
    album_artista = Album.query.filter(Album.artist_id == artist_id).all()
    
    lista_album = []
    all_tracks = []

    for album in album_artista:
        if album.id not in lista_album:
            lista_album.append(album.id)

    for album_id in lista_album:
        tracks_album = Track.query.filter(Track.album_id == album_id).all()
        all_tracks.append(tracks_album[0])
    
    try:
        for track in all_tracks:
            track.times_played += 1
            db.session.add(track)
    
    except ValidationError as errors:
        resp = jsonify(errors.messages)
        resp.status_code = 400
        return resp

    db.session.commit()
    resp = jsonify({"message": "You played all the albums of an artist"})

    return resp

@app.route("/albums/<album_id>/tracks/play", methods=["PUT"])
def play_album_tracks(album_id):
    all_tracks = Track.query.filter(Track.album_id == album_id).all()
    
    try:
        for track in all_tracks:
            track.times_played += 1
            db.session.add(track)
    
    except ValidationError as errors:
        resp = jsonify(errors.messages)
        resp.status_code = 400
        return resp

    db.session.commit()
    resp = jsonify({"message": "You played all the tracks of an album"})

    return resp

@app.route("/tracks/<track_id>/play", methods=["PUT"])
def play_track(track_id):
    track = Track.query.get_or_404(track_id)
    try:
        track.times_played += 1
    
    except ValidationError as errors:
        resp = jsonify(errors.messages)
        resp.status_code = 400
        return resp

    
    db.session.add(track)
    db.session.commit()

    resp = jsonify({"message": "You played a track"})

    return resp


#------------ DELETE ------------#


@app.route("/artists/<id>", methods=["DELETE"])
def delete_artist(id):
    artist = Artist.query.get_or_404(id)
    db.session.delete(artist)
    db.session.commit()
    resp = jsonify({"message": "deleted"})
    resp.status_code = 204
    return resp

@app.route("/albums/<id>", methods=["DELETE"])
def delete_album(id):
    album = Album.query.get_or_404(id)
    db.session.delete(album)
    db.session.commit()
    resp = jsonify({"message": "deleted"})
    resp.status_code = 204
    return resp

@app.route("/tracks/<id>", methods=["DELETE"])
def delete_track(id):
    track = Track.query.get_or_404(id)
    db.session.delete(track)
    db.session.commit()
    resp = jsonify({"message": "deleted"})
    resp.status_code = 204
    return resp

#------------ ERROR HANDLER ------------#

@app.errorhandler(404)
def page_not_found(error):
    resp = jsonify({"error": "not found"})
    resp.status_code = 404
    return resp


if __name__ == "__main__":
  
    if "createdb" in sys.argv:
        with app.app_context():
            db.create_all()
        print("Database created!")

    elif "seeddb" in sys.argv:  
        with app.app_context():

            a1 = Artist(id = "TWljaGFlbCBKYWNrc29u",
                        name = "Michael Jackson",
                        age = 21)
                        #albums = "https://apihost.com/artists/TWljaGFlbCBKYWNrc29u/albums")
                        #tracks = "https://apihost.com/artists/TWljaGFlbCBKYWNrc29u/tracks")
                        #self = "https://apihost.com/artists/TWljaGFlbCBKYWNrc29u")
            db.session.add(a1)

            al1 = Album(id = "T2ZmIHRoZSBXYWxsOlRXbG",
                        artist_id = "TWljaGFlbCBKYWNrc29u",
                        name = "Off the Wall",
                        genre = "Pop")
                        #artist = ,
                        #tracks = ,
                        #self = )

            db.session.add(al1)
            
            t1 = Track(id = "RG9uJ3QgU3RvcCAnVGlsIF",
                       album_id = "T2ZmIHRoZSBXYWxsOlRXbG",
                       name = "Don't Stop 'Til You Get Enough",
                       duration = 4.1,
                       times_played = 0)
                       #artist = ,  
                       #album = ,
                       #self = )

            db.session.add(t1)

            db.session.commit()
        print("Database seeded!")

    else:
        app.run(debug=True)
