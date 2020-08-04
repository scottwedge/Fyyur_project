#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import *
import sys

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
  
  venues = Venue.query.order_by(Venue.state, Venue.city).all()

  data = []
  tmp = {}
  prev_city = None
  prev_state = None
  for venue in venues:
    venue_data = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(list(filter(lambda x: x.start_time > datetime.today(),
                                            venue.shows)))
                  }
    if venue.city == prev_city and venue.state == prev_state:
      tmp['venues'].append(venue_data)
    else:
      if prev_city is not None:
        data.append(tmp)
        tmp['city'] = venue.city
        tmp['state'] = venue.state
        tmp['venues'] = [venue_data]
    prev_city = venue.city
    prev_state = venue.state

  data.append(tmp)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # 
  venue_query = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')) 
  response = {
    "count":venue_query.count(),
    "data": venue_query
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue= Venue.query.get(venue_id)
  upcoming_shows=[]
  past_shows=[]
  future_shows= db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  past= db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  for event in past:
    past_shows.append({
      "artist_id": event.artist_id,
      "artist_image_link" : event.artist.image_link,
      "start_time": event.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  for event in future_shows:
    upcoming_shows.append({
      "artist_id": event.artist_id,
      "artist_image_link" : event.artist.image_link,
      "start_time": event.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  

  data= {
    "id" : venue.id,
    "name" : venue.name,
    #"genres" : venue.genres,
    "address" : venue.address,
    "city" : venue.city,
    "state" : venue.state,
    "phone" : venue.phone,
    "website" : venue.website,
    "facebook_link" : venue.facebook_link,
    "seeking_talent" : venue.seeking_talent,
    "seeking_description" : venue.seeking_description,
    "image_link" : venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows" : upcoming_shows,
    "past_shows_count" : len(past_shows),
    "upcoming_shows_count" : len(upcoming_shows)
  }

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
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
  # # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # # TODO: on unsuccessful db insert, flash an error instead.
  # # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False
  try:
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres)
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    s_t = request.form.get('seeking_talent')
    if s_t=='y':
      venue.seeking_talent=True
    else:
      venue.seeking_talent=False
    venue.seeking_description = request.form['seeking_description']

    db.session.add(venue)
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

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error= False
  try:
    id= Venue.query.get(venue_id)
    db.session.delete(id)
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data= Artist.query.with_entities(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artist_query= Artist.query.filter(Artist.name.ilike('%'+ request.form['search_term'] + '%'))
  data=[]
  for all_artist in artist_query:
    data.append({
      "id": all_artist.id,
      "name": all_artist.name,
      "num_upcoming_shows" : db.session.query(Show).join(Artist).filter(Show.artist_id==all_artist_id).filter(Show.start_time>datetime,now()).count()
    })
  response={
    "count": artist_query.count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  all_artist= db.session.query(Artist).get(artist_id)
  past=db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now())
  future=db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now())
  past_shows=[]
  upcoming_shows=[]
  for event in past:
    past_shows.append({
      "venue_id": event.venue_id,
      "venue_name": event.venue.name,
      "venue_image_link":event.venue.image_link,
      "start_time":event.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  for event in future:
    upcoming_shows.append({
      "venue_id": event.venue_id,
      "venue_name": event.venue.name,
      "venue_image_link":event.venue.image_link,
      "start_time":event.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })  


  data={
    "id":all_artist.id,
    "name":all_artist.name,
    #"genres":all_artist.genres,
    "city":all_artist.city,
    "state": all_artist.state,
    "phone":all_artist.phone,
    "website": all_artist.website,
    "facebook_link" : all_artist.facebook_link,
    "seeking_venue" : all_artist.seeking_venue,
    "seeking_description" : all_artist.seeking_description,
    "image_link" : all_artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count" : len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.facebook_link.data = artist.facebook_link


  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artist = Artist()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()
    if error:
      flash('Artist could not be updated successfully')
    else:
      flash('Artist updated successfully!')


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()


  venue= Venue.query.get(artist_id)
  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_venue.data = venue.seeking_venue
    form.seeking_description.data = venue.seeking_description
  

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres)
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    s_t = request.form.get('seeking_talent')
    if s_t=='y':
      venue.seeking_talent=True
    else:
      venue.seeking_talent=False
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        flash('An error occured. Venue could not be updated!')
    else:
        flash('Venue was successfully updated.')  

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  error = False
  try:
    artist = Artist()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    artist.genres = ','.join(tmp_genres)
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    s_v = request.form.get('seeking_venue')
    if s_v=='y':
      artist.seeking_venue=True
    else :
      artist.seeking_venue=False
    artist.seeking_description = request.form['seeking_description']

    db.session.add(artist)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      abort (400)
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  
  all_shows= Show.query.all()
  data=[]
  for event in all_shows:
    data.append({
      "venue_id":event.venue_id,
      #"venue_name":event.venue_name,
      "artist_id":event.artist_id,
      # "artist_name":event.artist_name,
      # "artist_image_link":event.image_link,
      "start_time":event.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error= False
  try:
    show= Show()
    show.venue_id= request.form['venue_id']
    show.artist_id = request.form['artist_id']
    #image_link = request.form['image_link']
    start_time = request.form['start_time']
    db.session.add(show)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()
    if error:
      flash('An error occured. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
  # on successful db insert, flash success
  
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
