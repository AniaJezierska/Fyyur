#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request,   
    Response, 
    flash, 
    redirect, 
    url_for
)    
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    show = db.relationship('show', backref='venues', lazy=True)
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    show = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = "show"
  
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime())
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

db.create_all()  

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.  
  
  city_list = db.session.query(Venue.city, Venue.state).distinct()
  # list for storing venue data
  data = []

  for area in city_list:
  # add venues for city or state    
    venues = Venue.query.filter_by(city=area.city, state=area.state).all()
    venue_data = []
    
    data.append ({
      "city" : area.city,
      "state": area.state,
      "venues": venue_data
    })

    for venue in venues: 
    # get number of upcoming shows for each venue      
      num_upcoming_shows = 0
      shows_venue= Show.query.filter_by(venue_id=venue.id).all()
      for show in shows_venue:
        if show.start_time > datetime.now():
          num_upcoming_shows = num_upcoming_shows + 1

      venue_data.append ({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      }) 
  
  return render_template('pages/venues.html', areas=data);
  # return venues page with data

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # get the user search term
  search_term = request.form.get("search_term")
  # find all venues matching search term
  results = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []

  response = {
    "count": len(results),
    "data": data
  }  

  for venue in results:
    num_upcoming_shows = 0
    shows_venue = Show.query.filter(Show.venue_id==venue.id).all()
    for show in shows_venue:
    # count the number of upcoming concerts for the venue      
      if show.start_time > datetime.now():
        num_upcoming_shows = num_upcoming_shows + 1

    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    })      

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get("search_term"))
  # return response with search results

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id  
  
  #get a given venue
  venue = Venue.query.filter_by(id=venue_id).first()

  shows_venue = db.session.query(Artist.name, Artist.image_link, Show.venue_id, Show.artist_id, Show.start_time).join(Show, Show.artist_id == Artist.id).filter(Show.venue_id == venue_id)
  upcoming_shows = []
  past_shows = []

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "facebook_link": venue.facebook_link,
    "image_link": venue.image_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":  venue.seeking_description,
    "website": venue.website,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  #for upcoming show add show details 
  for show in shows_venue:
    if show.start_time > datetime.now():     
        upcoming_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
        })
  
  #for past show add show details 
  for show in shows_venue:
    if show.start_time < datetime.now():      
        past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))
        })    

  return render_template('pages/show_venue.html', venue=data)
  # return template with venue data


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion  
  error = False
  form = VenueForm()

  try:  
    # create new venue from form data
    venue = Venue(
        name=form.name.data, 
        city=form.city.data, 
        state=form.state.data, 
        address=form.address.data, 
        phone=form.phone.data, 
        genres=form.genres.data, 
        facebook_link=form.facebook_link.data, 
        image_link=form.image_link.data, 
        website=form.website.data, 
        seeking_talent=form.seeking_talent.data, 
        seeking_description=form.seeking_description.data
    )
    # add new venue to session and commit to database
    db.session.add(venue)
    db.session.commit()

    # on successful db insert, flash success 
    flash('Venue ' + request.form['name'] + ' was successfully listed!')      
  except: 
    # TODO: on unsuccessful db insert, flash an error instead.
    db.seesion.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')    
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ 
  finally:
    db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.  
  try:
   # delete venue and commit to data base  
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
# TODO: replace with real data returned from querying the database  
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".   
  search_term = request.form.get('search_term') 
  results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  data: []

  response = {
    "count": len(results),
    "data": data
  } 
  
  for artist in results:
    num_upcoming_shows = 0
    shows_artist = Show.query.filter(Show.artist_id==artist.id).all()
    for show in shows_artist:
      if show.start_time > datetime.now():
        num_upcoming_shows = num_upcoming_shows + 1

    data.append ({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get("search_term"))
  # return reponse with matching search results

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id  
  
  # get a given artis 
  artist = Artist.query.filter_by(id=artist_id).first()

  shows_artist = db.session.query(Venue.name, Venue.image_link, Show.venue_id, Show.artist_id, Show.start_time).join(Show, Show.venue_id == Venue.id).filter(Show.artist_id == artist_id)
  upcoming_shows = []
  past_shows = []

  # data for artist
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "address": artist.address,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "image_link": artist.image_link,
    "seeking_talent": artist.seeking_talent,
    "seeking_description":  artist.seeking_description,
    "website": artist.website,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  for show in shows_artist:
    if show.start_time > datetime.now():    
        upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.name,
          "venue_image_link": show.image_link,
          "start_time": format_datetime(str(show.start_time))
        })

  for show in shows_artist:
    if show.start_time < datetime.now():     
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.name,
          "venue_image_link": show.image_link,
          "start_time": format_datetime(str(show.start_time))
        })    

  return render_template('pages/show_venue.html', artist=data)
  # return artist page with data


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(obj=artist)

  if artist:
    form = ArtistForm(
      name=artist.name,
      genres=artist.genres,      
      city=artist.city,
      state=artist.state,
      phone=artist.phone,
      facebook_link=artist.facebook_link,
      image_link=artist.image_link,
      website=artist.website    
    )

    return render_template('forms/edit_artist.html', form=form, artist=artist)
    # return edit template with artist data

  # TODO: populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes  
  
  # get the artist by id
  artist = Artist.query.get(artist_id)

  try:    
    artist.name = request.form['name']
    artist.genres = request.form.getlist('genres')
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website = request.form['website']
    db.session.commit()
  except: 
      db.session.rollback()
  finally:
      db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

  # TODO: populate form with values from venue with ID <venue_id>


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
    form = VenueForm(
      name=venue.name,
      genres=venue.genres,
      city=venue.city,
      state=venue.state,
      address=venue.address,
      phone=venue.phone,
      facebook_link=venue.facebook_link,
      image_link=venue.image_link,
      website=venue.website,
    )

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes  
  error = False
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.genres = request.form.getlist('genres')
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    db.session.commit()  
  except:
    error = True
    db.session.rollback() 
  finally:
    db.session.close()
           
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
  form = ArtistForm()
  error = False
  try:
    artist = Artist(
      name=request.form['name'],
      genres=request.form.getlist('genres'),
      city=request.form['city'],
      state=request.form['state'],
      address = request.form['address'],
      phone=request.form['phone'],
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link'],
      website=request.form['website'],
    )
    db.session.add(artist)
    db.session.commit()
  except: 
    error = True
    db.seesion.rollback()
  finally:
    db.session.close()
    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    # on successful db insert, flash success
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows(): 
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.   
  data = []
  shows = Show.query.all()

  for show in shows:
  # get venue and artist information for show  
    data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link":Artist.query.get(show.artist_id).image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  return render_template('pages/shows.html', shows=data)
  # return shows page with show data


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.  
  form = ShowForm()

  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead  
  form = ShowForm()
  error = False

  try:
    show = Show(
      start_time=request.form['start_time'],
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id']
    )
    db.session.add(show)
    db.session.commit()
  except: 
    error = True
    db.seesion.rollback()
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/    
  if error:
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success 
  else:
    flash('Show was successfully listed!')

  return render_template('pages/home.html')

# error handlers
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
