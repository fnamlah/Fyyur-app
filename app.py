#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import os
# import psycopg2
from models import db, Venue, Artist, Show
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI
import collections
import collections.abc
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():

  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  """DONE"""
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # all_venues = db.session.query(Venue).all()
  # print(all_venues)
  # distinct_venues = Venue.query.distinct(Venue.city).all()
  areas = []

  distinct_locations = Venue.query.distinct(Venue.state).all()
  for location in distinct_locations:
      area = {}
      area['city'] = location.city
      area['state'] = location.state
      all_vens_city = Venue.query.filter_by(city=location.city, state=location.state).all()
      holder = []

      for ven in all_vens_city:
          item = {
              'id': ven.id,
              'name': ven.name
          }
          holder.append(item)
      area['venues'] = holder
      areas.append(area)


  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  #   """ALMOST DONE"""
  # # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # # seach for Hop should return "The Musical Hop".
  # # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '').title()
  print(search_term)
  response = Venue.query.filter(Venue.name.contains(search_term)).first()
  print(response)

  return render_template('pages/search_venues.html', venue=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  #   """DONE"""
  # # shows the venue page with the given venue_id
  # # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).first()
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #   """DONE"""
  # # TODO: insert form data as a new Venue record in the db, instead
  # # TODO: modify data to be the data object returned from db insertion
  # if form.validate():
  new_venue = Venue(name=request.form.get('name'), city=request.form.get('city'),
                    state=request.form.get('state'), address=request.form.get('address'), phone=request.form.get('phone'),
                    image_link=request.form.get('image_link'),
                    genres=request.form.get('genres'), facebook_link=request.form.get('facebook_link'),
                    website_link=request.form.get('website_link'), seeking_talent=request.form.get('seeking_talent', type=bool),
                    seeking_description=request.form.get('seeking_description'))
  db.session.add(new_venue)
  db.session.commit()

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE', 'GET'])
def delete_venue(venue_id):
    targeted_venue = Venue.query.filter_by(id=venue_id).first()
    print(targeted_venue)
    db.session.delete(targeted_venue)
    db.session.commit()

    return redirect('index')
    """DONE"""
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database: DONE
    all_artist = db.session.query(Artist).all()
    return render_template('pages/artists.html', artists=all_artist)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.: DONE
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '').title()
  response = Artist.query.filter(Artist.name.contains(search_term)).first()
  print(response)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  """DONE"""
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id: DONE
  target_artist = db.session.query(Artist).filter_by(id=artist_id).first()

  return render_template('pages/show_artist.html', artist=target_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_target = Artist.query.filter_by(id=artist_id).first()

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_target)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_target = Artist.query.filter_by(id=artist_id).first()
  print(artist_target)
  if request.method == 'POST':
      artist_target.name = request.form.get('name')
      artist_target.city = request.form.get('city')
      artist_target.state = request.form.get('state')
      artist_target.phone = request.form.get('phone')
      artist_target.image_link = request.form.get('image_link')
      artist_target.genres = request.form.get('genres')
      artist_target.facebook_link = request.form.get('facebook_link')
      artist_target.website_link = request.form.get('website_link')
      artist_target.seeking_venue = request.form.get('seeking_venue', type=bool)
      artist_target.seeking_description = request.form.get('seeking_description')

      db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.filter_by(id=venue_id).first()
  if request.method == 'POST':
      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.phone = request.form.get('phone')
      venue.image_link = request.form.get('image_link')
      venue.genres = request.form.get('genres')
      venue.facebook_link = request.form.get('facebook_link')
      venue.website_link = request.form.get('website_link')
      venue.seeking_talent = request.form.get('seeking_talent', type=bool)
      venue.seeking_description = request.form.get('seeking_description')
      db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  new_artist = Artist(name=request.form.get('name'),
                      city=request.form.get('city'),
                      state=request.form.get('state'),
                      phone=request.form.get('phone'),
                      genres=request.form.get('genres'),
                      facebook_link=request.form.get('facebook_link'),
                      image_link=request.form.get('image_link'),
                      website_link=request.form.get('website_link'),
                      seeking_venue=request.form.get('seeking_venue', type=bool),
                      seeking_description=request.form.get('seeking_description'))

  db.session.add(new_artist)
  db.session.commit()

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  all_shows = Show.query.all()
  return render_template('pages/shows.html', shows=all_shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  venue_id = Venue.query.get(request.form.get('venue_id'))
  artist_id = Artist.query.get(request.form.get('artist_id'))

  new_show = Show(venue=venue_id, artist=artist_id, start_time=request.form.get('start_time'))
  db.session.add(new_show)
  db.session.commit()

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''


