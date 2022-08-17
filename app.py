# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from os import abort
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    abort,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from forms import *
from operator import itemgetter  # for sorting lists of tuples
import re

# from crypt import methods
from models import Venue, Artist, Show
from utils import format_datetime, format_artist_venue

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
csrf = CSRFProtect(app)
moment = Moment(app)
# TODO: connect to a local postgresql database
app.config.from_object("config")
db = SQLAlchemy(app)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #  num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    venues = Venue.query.all()

    # A list of dictionaries, with city, state, and venues serving as the dictionary keys
    data = []

    # Make a set of all the cities and states that are unique.
    cities_states = set()
    for venue in venues:
        cities_states.add((venue.city, venue.state))  # Add tuple

    # Change cities_states set into an ordered list
    cities_states = list(cities_states)

    # Sorts on second column first (state), then by city.
    cities_states.sort(key=itemgetter(1, 0))

    now = datetime.now()

    # to add city/state locations to the data dictionary, loop through the distinct values.
    for loc in cities_states:
        # For this location, see if there are any venues there, and add if so
        venues_list = []
        for venue in venues:
            if (venue.city == loc[0]) and (venue.state == loc[1]):

                venue_shows = Show.query.filter_by(venue_id=venue.id).all()
                num_upcoming = 0
                for show in venue_shows:
                    if show.start_time > now:
                        num_upcoming += 1

                venues_list.append(
                    {
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": num_upcoming,
                    }
                )

        # After all venues are added to the list for a given location, add it to the data dictionary
        data.append({"city": loc[0], "state": loc[1], "venues": venues_list})

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "").strip()
    venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()

    data = [{"id": venue.id, "name": venue.name} for venue in venues]

    response = {"count": len(venues), "data": data}

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=search_term,
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)

    # The user must have manually entered a broken link into the browser.
    # Show 404 page
    if not venue:
        return abort(404)

    past_shows = (
        db.session.query(Show)
        .join(Venue)
        .filter(Show.venue_id == venue_id)
        .filter(Show.start_time < datetime.now())
        .all()
    )
    upcoming_shows = (
        db.session.query(Show)
        .join(Venue)
        .filter(Show.venue_id == venue_id)
        .filter(Show.start_time > datetime.now())
        .all()
    )

    data = format_artist_venue(venue, past_shows, upcoming_shows)
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm()
    error_in_update = False

    name = form.name.data.strip()
    genres = form.genres.data
    city = form.city.data.strip()
    state = form.state.data.strip()
    phone = form.phone.data.strip()
    phone = re.sub("\D", "", phone)
    address = form.address.data.strip()
    website = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()

    if not form.validate():
        flash(form.errors)
        return redirect(url_for("create_venue_submission"))
    else:
        error_in_update = False

    try:
        new_venue = Venue(
            name=name,
            genres=genres,
            city=city,
            state=state,
            phone=phone,
            address=address,
            website=website,
            facebook_link=facebook_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
            image_link=image_link,
        )

        db.session.add(new_venue)
        db.session.commit()

        # "website": "https://www.gunsnpetalsband.com",
        # "facebook_link": "https://www.facebook.com/GunsNPetals",
        # "seeking_venue": True,
        # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        # "image_link": "https:/
    except Exception as e:
        error_in_update = True
        print(f'Exception "{e}" in create_venue_submission()')
        db.session.rollback()
    finally:
        db.session.close()

    if not error_in_update:
        # on successful db insert, flash success
        # on successful db insert, flash success
        flash("Venue " + request.form["name"] + " was successfully listed!")
        return redirect(url_for("index"))
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash("An error occurred. Venue " + name + " could not be listed.")
        print("Error in create_venue_submission()")
        abort(500)


@app.route("/venues/<int:venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    print("Delete requested on id: " + venue_id)
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    venue = Venue.query.get(venue_id)

    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except Exception as e:
        print(f'Exception "{e}" in delete_venue()')
        db.session.rollback()
    finally:
        db.session.close()
        flash("Venue " + venue.name + " was successfully removed!")
        return redirect(url_for("/venues"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    return render_template(
        "pages/artists.html", artists=Artist.query.order_by("id").all()
    )


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get("search_term", "").strip()
    artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()

    data = [
        {
            "id": artist.id,
            "name": artist.name,
        }
        for artist in artists
    ]

    response = {"count": len(artists), "data": data}

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=search_term,
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.get(artist_id)

    # The user must have manually entered a broken link into the browser.
    # Show 404 page
    if not artist:
        abort(404)

    past_shows = (
        db.session.query(Show)
        .join(Venue)
        .filter(Show.artist_id == artist_id)
        .filter(Show.start_time < datetime.now())
        .all()
    )

    upcoming_shows = (
        db.session.query(Show)
        .join(Venue)
        .filter(Show.artist_id == artist_id)
        .filter(Show.start_time > datetime.now())
        .all()
    )

    data = format_artist_venue(artist, past_shows, upcoming_shows)

    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    # artist.phone = artist.phone[:3] + "-" + artist.phone[3:6] + "-" + artist.phone[6:]
    form = ArtistForm(obj=artist)

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    error_inserting_db = False

    name = form.name.data.strip()
    genres = form.genres.data
    city = form.city.data.strip()
    state = form.state.data.strip()
    phone = form.phone.data.strip()
    phone = re.sub("\D", "", phone)
    website = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()

    if not form.validate():
        flash(form.errors)
        return redirect(url_for("edit_artist_submission", artist_id=artist_id))
    else:
        error_inserting_db = False

    try:
        artist = Artist.query.get(artist_id)

        artist.name = name
        artist.genres = genres
        artist.city = city
        artist.state = state
        artist.phone = phone
        artist.website = website
        artist.facebook_link = facebook_link
        artist.seeking_venue = seeking_venue
        artist.seeking_description = seeking_description
        artist.image_link = image_link

        db.session.commit()

    except Exception as e:
        error_inserting_db = True
        print(f'Exception "{e}" in edit_artist_submission()')
        db.session.rollback()

    if not error_inserting_db:
        # on successful db insert, flash success
        flash("Artist " + name + " was successfully updated!!")
        return redirect(url_for("show_artist", artist_id=artist_id))
    else:
        flash("An error occurred. Artist " + name + " could not be updated.")
        return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

    print(form.seeking_talent.data)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    error_in_updating = False

    name = form.name.data.strip()
    genres = form.genres.data
    city = form.city.data.strip()
    state = form.state.data.strip()
    phone = form.phone.data.strip()
    phone = re.sub("\D", "", phone)
    address = form.address.data.strip()
    website = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()

    if not form.validate():
        flash(form.errors)
        return redirect(url_for("edit_venue_submission", venue_id=venue_id))
    else:
        error_in_updating = False

    try:
        venue = Venue.query.get(venue_id)

        venue.name = name
        venue.genres = genres
        venue.city = city
        venue.state = state
        venue.phone = phone
        venue.phone = phone
        venue.address = address
        venue.website = website
        venue.facebook_link = facebook_link
        venue.seeking_talent = seeking_talent
        venue.seeking_description = seeking_description
        venue.image_link = image_link

        db.session.commit()

    except Exception as e:
        error_in_updating = True
        print(f'Exception "{e}" in edit_venue_submission()')
        db.session.rollback()

    if not error_in_updating:
        # on successful db insert, flash success
        flash("Venue " + name + " was successfully updated!!")
        return redirect(url_for("show_venue", venue_id=venue_id))
    else:
        flash("An error occurred. Venue " + name + " could not be updated.")
        return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm()

    error = False

    name = form.name.data.strip()
    genres = form.genres.data
    city = form.city.data.strip()
    state = form.state.data.strip()
    phone = form.phone.data.strip()
    phone = re.sub("\D", "", phone)
    website = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()

    if not form.validate():
        flash(form.errors)
        return redirect(url_for("create_artist_submission"))
    else:
        error = False

    try:
        new_artist = Artist(
            name=name,
            genres=genres,
            city=city,
            state=state,
            phone=phone,
            website=website,
            facebook_link=facebook_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
            image_link=image_link,
        )

        db.session.add(new_artist)
        db.session.commit()

        # "website": "https://www.gunsnpetalsband.com",
        # "facebook_link": "https://www.facebook.com/GunsNPetals",
        # "seeking_venue": True,
        # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        # "image_link": "https:/
    except Exception as e:
        error = True
        print(f'Exception "{e}" in create_artist_submission()')
        db.session.rollback()
    finally:
        db.session.close()

    if not error:
        # on successful db insert, flash success
        flash("Artist " + request.form["name"] + " was successfully listed!")
        return redirect(url_for("index"))
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Artist " + name + " could not be listed.")
        print("Error in create_artist_submission()")
        abort(500)


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []

    shows = Show.query.order_by("id").all()

    for show in shows:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": format_datetime(str(show.start_time)),
            }
        )

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm()

    error_inserting_db = False

    artist_id = form.artist_id.data.strip()
    venue_id = form.venue_id.data.strip()
    start_time = form.start_time.data

    if not form.validate():
        flash(form.errors)
        return redirect(url_for("create_show_submission"))
    else:
        error_inserting_db = False

    try:
        new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(new_show)
        db.session.commit()
    except Exception as e:
        error_inserting_db = True
        print(f'Exception "{e}" in create_show_submission()')
        db.session.rollback()
    finally:
        db.session.close()

    if not error_inserting_db:
        # on successful db insert, flash success
        flash("Show was successfully listed!")
        return redirect(url_for("index"))
    else:

        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        print("Error in create_show_submission()")
        abort(500)


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
