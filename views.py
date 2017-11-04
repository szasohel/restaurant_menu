from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, Catagory, User, Item
from flask import Flask, render_template, url_for, flash, jsonify
from flask import request, redirect
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

# connect to database
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

# create database session

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "catalog application"


# Create anti-forgery state token
@app.route('/login')
def show_login():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:'
    output += '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully disconnected")
        return redirect(url_for('show_catagory'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# show all catagory
@app.route('/')
@app.route('/catagory/')
def show_catagory():
    catagories = session.query(Catagory).order_by(asc(Catagory.name))
    if 'username' not in login_session:
        return render_template('public_catagory.html', catagories=catagories)
    else:
        return render_template('catagory.html', catagories=catagories)


# add new catagory
@app.route('/catagory/new', methods=['GET', 'POST'])
def new_catagory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_name = request.form['name']
        new_catagory = Catagory(name=new_name,
                                user_id=login_session['user_id'])
        session.add(new_catagory)
        session.commit()
        return redirect(url_for('show_catagory'))
    else:
        return render_template('new_catagory.html')


# delete existing catagory
@app.route('/catagory/<int:catagory_id>/delete/', methods=['GET', 'POST'])
def delete_catagory(catagory_id):
    catagory_delete = session.query(Catagory).filter_by(id=catagory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catagory_delete.user_id != login_session['user_id']:
        flash('You are not authorized to delete %s' % catagory_delete.name)
        return redirect(url_for('show_item', catagory_id=catagory_delete.id))
    if request.method == 'POST':
        session.delete(catagory_delete)
        session.commit()
        return redirect(url_for('show_catagory'))
    else:
        return render_template(
                            'delete_catagory.html', catagory=catagory_delete)


# edit existing catagory
@app.route('/catagory/<int:catagory_id>/edit/', methods=['GET', 'POST'])
def edit_catagory(catagory_id):
    catagory_edit = session.query(Catagory).filter_by(id=catagory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catagory_edit.user_id != login_session['user_id']:
        flash('You are not authorized to edit %s' % catagory_edit.name)
        return redirect(url_for('show_item', catagory_id=catagory_edit.id))
    if request.method == 'POST':
        if request.form['name']:
            catagory_edit.name = request.form['name']
            return redirect(url_for('show_catagory'))
    else:
        return render_template('edit_catagory.html', catagory=catagory_edit)


# show all items
@app.route('/catagory/<int:catagory_id>/items/')
def show_item(catagory_id):
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    items = session.query(Item).filter_by(catagory_id=catagory_id).all()

    if 'username' not in login_session:
        return render_template(
                        'public_items.html', catagory=catagory, items=items)
    else:
        return render_template('items.html', catagory=catagory, items=items)


# create new items
@app.route('/catagory/<int:catagory_id>/items/new/', methods=['GET', 'POST'])
def new_item(catagory_id):
    if 'username' not in login_session:
        return redirect('/login')
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()

    if request.method == 'POST':
        item_name = request.form['name']
        item_desc = request.form['description']
        new_item = Item(name=item_name, description=item_desc,
                        catagory_id=catagory.id,
                        user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        return redirect(url_for('show_item', catagory_id=catagory.id))
    else:
        return render_template('new_item.html', catagory=catagory)


# edit existing items
@app.route('/catagory/<int:catagory_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def edit_item(catagory_id, item_id):
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    item = session.query(Item).filter_by(id=item_id).one()

    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        flash('You are not authorized to edit %s' % item.name)
        return redirect(url_for('show_item', catagory_id=catagory.id))

    if request.method == 'POST':
        if request.form['name'] or request.form['description']:
            item.name = request.form['name']
            item.description = request.form['description']
            return redirect(url_for('show_item', catagory_id=catagory.id))
    else:
        return render_template('edit_item.html', catagory=catagory, item=item)


# delete existing items
@app.route('/catagory/<int:catagory_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def delete_item(catagory_id, item_id):
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    item = session.query(Item).filter_by(id=item_id).one()

    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        flash('You are not authorized to delete %s' % item.name)
        return redirect(url_for('show_item', catagory_id=catagory.id))

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('show_item', catagory_id=catagory.id))
    else:
        return render_template('delete_item.html',
                               catagory=catagory, item=item)


# JSON APIs to view catalog Information
@app.route('/catagory/<int:catagory_id>/item/JSON')
def itemJSON(catagory_id):
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    items = session.query(Item).filter_by(catagory_id=catagory_id).all()
    return jsonify(Item=[i.serialize for i in items])


@app.route('/catagory/JSON')
def catagoryJSON():
    catagory = session.query(Catagory).all()
    return jsonify(Catagory=[r.serialize for r in catagory])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run()
