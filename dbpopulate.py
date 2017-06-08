from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbsetup import Category, Base, User, Items

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy users
user1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()

user2 = User(name="John Legend", email="johnlegend@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user2)
session.commit()

# Items for Soccer
category1 = Category(name="Soccer")

session.add(category1)
session.commit()

item1 = Items(user_id=1, name="Soccer Gloves", description="Strong grippy soccer gloves.",
                     category_name="Soccer")

session.add(item1)
session.commit()

item2 = Items(user_id=2, name="Soccer Ball", description="Official FIFA World Cup ball.",
                     category_name="Soccer")

session.add(item2)
session.commit()

# Items for Baseball
category2 = Category(name="Baseball")

session.add(category2)
session.commit()

item3 = Items(user_id=1, name="Baseball", description="Fast speedy baseball.",
                     category_name="Baseball")

session.add(item3)
session.commit()

item4 = Items(user_id=1, name="Baseball Bat", description="Perfect for the zombie apocalypse.",
                     category_name="Baseball")

session.add(item4)
session.commit()

print "added catalog items!"
