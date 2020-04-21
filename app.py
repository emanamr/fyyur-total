#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import datetime
import babel
from flask_moment import Moment
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter
from logging import FileHandler
from flask_wtf import Form
from forms import *
import config
from flask_migrate import Migrate
from sqlalchemy import or_
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config') 
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500) )
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    shows = db.relationship('Show', backref=db.backref("venue_shows" , lazy=True))
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref=db.backref("artist_shows" , lazy=True))

    #venues = db.relationship('Venues', secondary=Show, backref=db.backref('artists', lazy=True)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    venue_id = db.Column(db.Integer , db.ForeignKey(Venue.id))
    artist_id = db.Column(db.Integer , db.ForeignKey(Artist.id))

    
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

# -------------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue
    
  
    areas = Venue.query.distinct('city','state').all()
    data = []
    city=Venue.city
    state=Venue.state
    for area in areas:
      venues = Venue.query.filter_by(city = area.city, state = area.state).all()
      for venue in venues:
                   id=venue.id
                   name=venue.name
      record = {
        'city': area.city,
        'state': area.state,
        'venues': [{"id":id,
                   "name":name }]}
      data.append(record)
    return render_template('pages/venues.html', areas=data )
          
#######find venue by search----------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    
    search_term=request.form.get('search_term').lower()
    search= "%{}%".format(search_term)
    data = Venue.query.filter(or_(Venue.name.ilike(search),
                                    Venue.state.ilike(search),
                                    Venue.city.ilike(search))).all()
    count = Venue.query.filter(or_(Venue.name.ilike(search),
                                    Venue.state.ilike(search),
                                    Venue.city.ilike(search))).count()
    for d in data:
        response={
            "data":[{
                "id":d.id,
                "name":d.name}],
            "count":count}
  
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
##show venue page by his id---------------------------

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    data=Venue.query.get(venue_id)
    venue = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows =upcoming_shows = []
    count_past=count_upcoming=0
    for show in shows:
      if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M') < datetime.now():
        past_shows=({
          "artist_id": show.artist_id,
          "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
          "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
          "start_time": show.start_time
        })
        count_past+=1
      elif datetime.strptime(show.start_time, '%Y-%m-%d %H:%M')> datetime.now():
        upcoming_shows=({
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": show.start_time
          })
        count_upcoming+=1
      
    data = {

        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "city": venue.city,
        "state": venue.state,
        "address": venue.address,
        "phone": venue.phone,
        "website_link": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": count_past,
        "upcoming_shows_count": count_upcoming
    }
    return render_template('pages/show_venue.html', venue=data)

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
    
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres,
                    image_link=image_link, facebook_link = facebook_link)
    try:
        db.session.add(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form.get('name') + ' was successfully listed!')

    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    finally:
        db.session.close()
    return render_template('pages/home.html')

#-----------------------------------------------------------------  
###delete venue

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    Venue.query.filter_by(id=venue_id).delete()
    try:
        db.session.commit()
        flash('Venue was successfully deleted!')
    except:
        db.session.rollback()
        flash("Venue wasn't ")
    finally:
        db.session.close()
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    id=Artist.id
    data = Artist.query.order_by(id).all()


    return render_template('pages/artists.html', artists=data)
#-----------------------------------------------------------------------------------
###find artist by search 

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  
    srch_term=request.form.get('search_term').lower()
    search= "%{}%".format(srch_term)
    
    data = Artist.query.filter(or_(Artist.name.ilike(search),
                                    Artist.state.ilike(search),
                                    Artist.city.ilike(search))).all()
    count = Artist.query.filter(or_(Artist.name.ilike(search),
                                    Artist.state.ilike(search),
                                    Artist.city.ilike(search))).count()
    
    for d in data:
    
         response={
            "count": count,
            "data": [{
              "id": d.id,
              "name": d.name
            }]
  }

    return render_template('pages/search_artists.html', results = response, search_term=request.form.get('search_term',''))
#-------------------------------------------------------------------------------------
######show artist page by id

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    shows = Show.query.filter_by(artist_id=artist_id).all()
    past_shows =upcoming_shows = []
    count_past=count_upcoming=0
    for show in shows:
      if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M') < datetime.now():
        past_shows=({
          "artist_id": show.artist_id,
          "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
          "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
          "start_time": show.start_time
        })
        count_past+=1
      elif datetime.strptime(show.start_time, '%Y-%m-%d %H:%M')> datetime.now():
        upcoming_shows=({
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": show.start_time
          })
        count_upcoming+=1
      
    data = {

        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website_link": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": count_past,
        "upcoming_shows_count": count_upcoming
    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                    image_link=image_link, facebook_link = facebook_link)
    try:
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()


    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres,
                    image_link=image_link, facebook_link = facebook_link)
    try:
        db.session.commit()
    except:
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
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                    image_link=image_link, facebook_link = facebook_link)
    try:
        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form.get('name') + ' was successfully listed!')

    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    finally:
        db.session.close()
    return render_template('pages/home.html')

#-------------------------------------------------------------------    
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    data=[]
    shows = Show.query.all()

    for show in shows:

        
        data.append({
        "venue_id": show.venue_id,
        "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link":Artist.query.filter_by(id=show.artist_id).first().image_link ,
        "start_time":str( show.start_time) })
  
    return render_template('pages/shows.html', shows=data)

#=========================================================================================

   
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    id = request.form.get('id')
    start_time = request.form.get('start_time')
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    show = Show(id=id, start_time=start_time, venue_id=venue_id, artist_id = artist_id)
    try:
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    finally:
        db.session.close()
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
