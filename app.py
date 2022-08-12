#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import desc
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import ValidationError, DataRequired, url
from models import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#db = SQLAlchemy(app)
db.init_app(app)
Migrate(app,db)

# TODO: connect to a local postgresql database

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/venues.html', venu = Venue.query.order_by(desc('id')).all());

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  results= Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  resultss= Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).count()

  return render_template('pages/search_venues.html', search_term=search_term, results=results,county=resultss )

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

 # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
 upcoming_shows_query = db.session.query(Show.start_time, Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image')).join(Artist).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
 past_shows_query = db.session.query(Show.start_time, Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image')).join(Artist).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
 return render_template('pages/show_venue.html', upcoming = upcoming_shows_query, past_show = past_shows_query, venue = Venue.query.get(venue_id))


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
    try:
        new_venue = Venue()
        new_venue.name = request.form.get('name')
        new_venue.city = request.form.get('city')
        new_venue.state = request.form.get('state')
        new_venue.address = request.form.get('address')
        new_venue.phone = request.form.get('phone')
        tmp_genres = request.form.getlist('genres')
        new_venue.genres = ','.join(tmp_genres)
        new_venue.facebook_link = request.form.get('facebook_link')
        new_venue.website_link= request.form.get('website_link')
        new_venue.image_link = request.form.get('image_link')
        new_venue.seeking_talent = request.form.get('seeking_talent')
        new_venue.seeking_description = request.form.get('seeking_description')
        db.session.add(new_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' +
                  request.form['name'] + ' Could not be listed!')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
    return render_template('pages/home.html')


  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
 # return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  query = db.session.query(Show.start_time, Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link, Venue.id.label('venue_id'), Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link') ).join(Artist, Artist.id==Show.artist_id).join(Venue, Venue.id==Show.venue_id).all()
  return render_template('pages/artists.html', artists = Artist.query.all(), artisty=query )

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search=request.form.get('search_term', '')

  #response=Artist.query.filter(Artist.name.ilike(f"%{search}%")).all()
  results= Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()
  resultss= Artist.query.filter(Artist.name.ilike(f'%{search}%')).count()
  #response = Artist.query.filter(Artist.name.match("%search%")).all()

  return render_template('pages/search_artists.html', search_term=search, results=results, county=resultss)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  #query_upcoming = db.session.query(Show.start_time, Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link, Venue.id.label('venue_id'), Venue.name.label('venue_name') ).join(Artist, Artist.id==Show.artist_id).join(Venue, Venue.id==Show.venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_query = db.session.query(Show.start_time, Venue.id.label('venue_id'), Venue.name.label('venue_name'), Venue.image_link.label('artist_image')).join(Artist).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  past_shows_query = db.session.query(Show.start_time, Venue.id.label('venue_id'), Venue.name.label('venue_name'), Venue.image_link.label('artist_image')).join(Artist).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  return render_template('pages/show_artist.html', upcoming_show = upcoming_shows_query, past_show=past_shows_query, artist=Artist.query.get(artist_id))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)

    error = False
    try:
        
        update_artist = Artist.query.get(artist_id)

        update_artist.name = form.name.data
        update_artist.city = form.city.data
        update_artist.state = form.state.data
        update_artist.phone = request.form['phone']
        update_artist.genres=",".join(form.genres.data)
        update_artist.facebook_link = form.facebook_link.data
        update_artist.image_link = form.image_link.data
        #new_artist.seeking_venue = request.form['seeking_venue']
        #new_artist.seeking_description = request.form['seeking_description']
        db.session.add(update_artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Artist ' +
                  request.form['name'] + ' Could not be updated!')
        else:
            flash('Artist ' + request.form['name'] +
                  ' was successfully updated!')


    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)

    error = False
    try:
        
        update_venue = Venue.query.get(venue_id)

        update_venue.name = form.name.data
        update_venue.city = form.city.data
        update_venue.state = form.state.data
        update_venue.address = form.address.data
        update_venue.genres=",".join(form.genres.data)
        update_venue.facebook_link = form.facebook_link.data
        update_venue.image_link = form.image_link.data
        update_venue.website_link = form.website_link.data
        update_venue.seeking_venue = form.seeking_talent.data
        update_venue.seeking_description = form.seeking_description.data
        db.session.add(update_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' +
                  request.form['name'] + ' Could not be updated!')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')

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

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

    error = False
    try:
        new_artist = Artist()
        new_artist.name = request.form['name']
        new_artist.city = request.form['city']
        new_artist.state = request.form['state']
        new_artist.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        new_artist.genres = ','.join(tmp_genres)
        new_artist.facebook_link = request.form['facebook_link']
        new_artist.image_link = request.form['image_link']
        #new_artist.seeking_venue = request.form['seeking_venue']
        #new_artist.seeking_description = request.form['seeking_description']
        db.session.add(new_artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Artist ' +
                  request.form['name'] + ' Could not be listed!')
        else:
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
    
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  query = db.session.query(Show.start_time, Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link, Venue.id.label('venue_id'), Venue.name.label('venue_name') ).join(Artist, Artist.id==Show.artist_id).join(Venue, Venue.id==Show.venue_id).all()
  return render_template('pages/shows.html', shows = query)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    error = False
    try:
        new_show = Show()
        new_show.artist_id = request.form['artist_id']
        new_show.venue_id = request.form['venue_id']
        new_show.start_time = request.form['start_time']
        db.session.add(new_show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('Show was not successfully listed!')
        else:
            flash('Show was successfully listed!')

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
