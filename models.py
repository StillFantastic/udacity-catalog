from wtforms import Form, StringField, IntegerField, PasswordField, validators, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import AnyOf, Length
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, User, Category, Items

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
categories = session.query(Category).order_by(asc(Category.name))
category_names = []
category_choices = []

for category in categories:
    category_names.append(category.name)
    category_choices.append((category.name,category.name))

class AddItemForm(Form):
    name = StringField('Name', validators=[Length(min=1, max=50)])
    description = StringField('Description', widget=TextArea(), validators=[Length(min=1, max=250)])
    category = SelectField('Category', choices=category_choices, validators=[validators.AnyOf(category_names)])