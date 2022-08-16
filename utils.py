import dateutil.parser
import babel


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


def format_show(show):
    return {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "venue_image_link": show.venue.image_link,
        "start_time": format_datetime(str(show.start_time)),
    }


def format_shows(shows):
    formatted_shows = []
    for show in shows:
        formatted_shows.append(format_show(show))
    return formatted_shows


def format_artist_venue(artist_venue, past_shows, upcoming_shows):
    data = artist_venue.__dict__
    data["past_shows"] = format_shows(past_shows)
    data["upcoming_shows"] = format_shows(upcoming_shows)
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)
    return data
