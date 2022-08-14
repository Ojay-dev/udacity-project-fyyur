from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.PickleType, nullable=False)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    shows = db.relationship("Show", backref="venue", lazy=True)

    def __repr__(self):
        return f"<Venue {self.id}, name:{self.name}, city:{self.city}, state:{self.state}, address:{self.address}, image_link:{self.image_link}, facebook_link:{self.facebook_link}, genres:{self.genres}, website:{self.website}, seeking_talent:{self.seeking_talent}, seeking_description:{self.seeking_description}, shows:{self.shows}>"


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.PickleType, nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    shows = db.relationship("Show", backref="artist", lazy=True)

    def __repr__(self):
        return f"<Venue {self.id}, name:{self.name}, city:{self.city}, state:{self.state}, image_link:{self.image_link}, facebook_link:{self.facebook_link}, genres:{self.genres}, website:{self.website}, seeking_talent:{self.seeking_venue}, seeking_description:{self.seeking_description}, shows:{self.shows}>"


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String) #TODO: implement later (not a requirement now)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    start_time = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )  # Start time required field

    def __repr__(self):
        return f"<Todo {self.id}, venue_id:{self.venue_id}, artist_id:{self.artist_id}, start_time:{self.start_time}>"
