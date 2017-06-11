# Item Catalog

## Introduction
Project for Udacity Full Stack Webdeeloper Nanodegree. Built on Flask and SQLite.

## Description
Catalog is a database of items grouped by catagories. Users can perform CRUD operations on their own
items. Authentication is via Facebook Login.

## Quickstart
1. Git clone the repository and cd into it.
2. If you haven't already, [install pip](https://pip.pypa.io/en/stable/installing/).
3. (Optional) Install virtualenv and activate the virtual environment. `pip install virtualenv` `virtualenv ENV` `source ENV/bin/activate`
4. Install the dependencies. `pip install -r requirements.txt`
5. Setup the database. `python dbsetup.py`
6. Modify the categories in CATEGORIES in `dbpopulate.py` before running `python dbpopulate.py`
7. Modifiy app.secret_key in app.py
8. Run the app. `python app.py`

## Usage
* Login by clicking the 'Login' link and logging in via Facebook
* Once logged in, you will see view, edit, and delete buttons beside each item row in the catalog
* To view the JSON output, go to `/catalog/<item_id>/JSON`


