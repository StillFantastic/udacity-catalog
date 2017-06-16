from dbsetup import Base, User, Category, Items
from flask import Flask, render_template, request, redirect, jsonify, url_for,\
     flash, make_response
from flask import session as login_session
from functools import wraps
from models import ItemForm
from sqlalchemy import create_engine, asc, desc, or_
from sqlalchemy.orm import sessionmaker, sessionmaker
import httplib2
import json
import random
import requests
import string

app = Flask(__name__)
app.secret_key = 'super_secret_key'

APPLICATION_NAME = "Item Catalog"

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            flash('You are not logged in. Please login.', 'danger')
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


# Show categories and items
@app.route('/')
@app.route('/catalog/')
def index():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Items).order_by(desc(Items.id))
    if 'username' not in login_session:
        return render_template('index.html', categories=categories,
                               category_name='All Items', items=items)
    else:
        return render_template('index.html', categories=categories,
                               category_name='All Items', items=items)


# Show items under category
@app.route('/catalog/<string:category_name>/')
def categoryItems(category_name):
    category_name = category_name.title()
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Items).filter_by(category_name=category_name).\
        order_by(desc(Items.id))
    if 'username' not in login_session:
        return render_template('category.html', categories=categories,
                               category_name=category_name, items=items)
    else:
        return render_template('category.html', categories=categories,
                               category_name=category_name, items=items)


# Create an item
@app.route('/catalog/new/', methods=['GET', 'POST'])
@login_required
def newItem():
    form = ItemForm(request.form)
    if request.method == 'POST':
        if form.validate():
            newItem = Items(name=form.name.data,
                            description=form.description.data,
                            category_name=form.category_name.data,
                            user_id=login_session['user_id'])
            session.add(newItem)
            flash('New Item %s Successfully Created' % newItem.name, 'success')
            session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('itemForm.html', action="Create", form=form,
                                   url=url_for('newItem'))
    else:
        return render_template('itemForm.html', action="Create", form=form,
                               url=url_for('newItem'))


# View an item
@app.route('/catalog/<int:item_id>/')
def viewItem(item_id):
    categories = session.query(Category).order_by(asc(Category.name))
    item = session.query(Items).filter_by(id=item_id).one()
    category_name = item.category_name
    if 'username' not in login_session:
        return render_template('item.html', categories=categories,
                               category_name=category_name, item=item)
    else:
        return render_template('item.html', categories=categories,
                               category_name=category_name, item=item)


# Edit an item
@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item_id):
    editedItem = session.query(Items).filter_by(id=item_id).one()
    form = ItemForm(request.form, obj=editedItem)

    if login_session['user_id'] != editedItem.user_id:
        flash('You are not authorized to edit this item. Please create your own\
              item in order to edit.', 'danger')
        return redirect('/')
    if request.method == 'POST':
        form = ItemForm(request.form)
        if form.validate():
            editedItem.name = form.name.data
            editedItem.description = form.description.data
            editedItem.category_name = form.category_name.data
            session.commit()
            flash('Item Successfully Edited', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('itemForm.html', action="Edit", form=form,
                                   url=url_for('editItem', item_id=item_id))
    else:
        return render_template('itemForm.html', action="Edit", form=form,
                               url=url_for('editItem', item_id=item_id))


# Delete an item
@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_id):
    itemToDelete = session.query(Items).filter_by(id=item_id).one()

    if itemToDelete.user_id != login_session['user_id']:
        flash('You are not authorized to delete this item. Please create your \
            own item in order to delete.', 'danger')
        return redirect('/')

    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('%s Successfully Deleted' % itemToDelete.name, 'success')
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


# Search for items by finding matches in name, description, and category
@app.route('/search')
def data():
    query = request.args.get('q')
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Items).filter(or_(Items.name.contains(query),
                                        Items.description.contains(query),
                                        Items.category_name.contains(query)))\
        .order_by(desc(Items.id))
    print query
    return render_template('index.html', categories=categories,
                           category_name='Search Results', items=items)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    if 'username' in login_session:
        flash('You are already logged in.', 'danger')
        return redirect('/')
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


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


# JSON APIs to view Item Information
@app.route('/catalog/<int:item_id>/JSON')
def itemJSON(item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'\
        % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we
        have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email'\
        % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200'\
        % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'], 'success')
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s'\
        % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.", 'success')
        return redirect('/')
    else:
        flash("You were not logged in.")
        return redirect('/', 'danger')


if __name__ == '__main__':
    app.run()
