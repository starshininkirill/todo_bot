# main.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre = fields.Str()
    director = fields.Str()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()

directors_schema = DirectorSchema(many=True)
director_schema = DirectorSchema()

api = Api(app)
api.app.config["RESTX_JSON"] = {'ensure_ascii': False, 'indent': 4}
movies_ns = api.namespace("movies")
director_ns = api.namespace("directors")


@movies_ns.route("/")
class MoviesViews(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if genre_id != None and director_id != None:
            all_movies = db.session.query(Movie).filter(Movie.director_id == director_id, Movie.genre_id == genre_id).all()
        elif director_id:
            all_movies = db.session.query(Movie).filter(Movie.director_id == director_id).all()
        elif genre_id:
            all_movies = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()
        else:
            all_movies = db.session.query(Movie).all()
        movies = movies_schema.dump(all_movies)
        return movies, 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movies_ns.route("/<int:mid>")
class MovieViews(Resource):
    def get(self, mid):
        movie_model = db.session.query(Movie).filter(Movie.id == mid).one()
        movie = movie_schema.dump(movie_model)
        return movie, 200

    def delete(self, mid):
        try:
            movie_model = db.session.query(Movie).get(mid)
            db.session.delete(movie_model)
            db.session.commit()
            return "", 204
        except Exception as e:
            return "Такого фильма не существует", 404

    # def put(self, mid):
    #     req_json = request.json
    #     movie = db.session.query(Movie).get(mid)
    #     if movie is None:
    #         return "Такого фильма не существует"
    #     else:


@director_ns.route("/")
class DirectorsViews(Resource):
    def post(self):
        req_json = request.json
        db.session.add(Director(**req_json))
        db.session.commit()
        return "", 201


@director_ns.route("/<int:did>")
class DirectorViews(Resource):
    def delete(self, did):
        if db.session.query(Director).get(did) is None:
            return "Такого режисера не существует", 401
        else:
            director = db.session.query(Director).get(did)
            db.session.delete(director)
            db.session.commit()
            return "", 201

    def get(self, did):
        if db.session.query(Director).get(did) is None:
            return "Такого режисёра не существует"
        else:
            director_model = db.session.query(Director).get(did)
            director = director_schema.dump(director_model)
            return director, 200

    def put(self, did):
        req_json = request.json
        if db.session.query(Director).get(did) is None:
            return "Такого режисёра не существует", 401
        else:
            director_model = db.session.query(Director).get(did)
            director_model.id = req_json['id']
            director_model.name = req_json['name']
            db.session.commit()
            return "", 201


if __name__ == '__main__':
    app.run(debug=True)
