from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Catagory, Base, Item, User

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



User1 = User(name="sayed sohel", email="sayedctg06@yahoo.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


Catagory2 = Catagory(name="Beverages")

session.add(Catagory2)
session.commit()

Item2 = Item(name="item2", description="Item description goes here", catagory=Catagory2)

session.add(Item2)
session.commit()


Item1 = Item(name="item1", description="Item description goes here", catagory=Catagory2)

session.add(Item1)
session.commit()

Item3 = Item(name="item3", description="Item description goes here", catagory=Catagory2)

session.add(Item3)
session.commit()

Item4 = Item(name="item4", description="Item description goes here", catagory=Catagory2)

session.add(Item4)
session.commit()

Item5 = Item(name="item5", description="Item description goes here", catagory=Catagory2)

session.add(Item5)
session.commit()

Item6 = Item(name="item6", description="Item description goes here", catagory=Catagory2)

session.add(Item6)
session.commit()

Item7 = Item(name="item7",
                     description="Item description goes heree", catagory=Catagory2)

session.add(Item7)
session.commit()

Item8 = Item(name="item8", description="Item description goes here", catagory=Catagory2)

session.add(Item8)
session.commit()

Catagory3 = Catagory(name="Groceries")

session.add(Catagory3)
session.commit()

Item2 = Item(name="item2", description="Item description goes here", catagory=Catagory3)

session.add(Item2)
session.commit()


Item1 = Item(name="item1", description="Item description goes here", catagory=Catagory3)

session.add(Item1)
session.commit()

Item3 = Item(name="item3", description="Item description goes here", catagory=Catagory3)

session.add(Item3)
session.commit()

Item4 = Item(name="item4", description="Item description goes here", catagory=Catagory3)

session.add(Item4)
session.commit()

Item5 = Item(name="item5", description="Item description goes here", catagory=Catagory3)

session.add(Item5)
session.commit()

Item6 = Item(name="item6", description="Item description goes here", catagory=Catagory3)

session.add(Item6)
session.commit()

Item7 = Item(name="item7",
                     description="Item description goes heree", catagory=Catagory3)

session.add(Item7)
session.commit()

Item8 = Item(name="item8", description="Item description goes here", catagory=Catagory3)

session.add(Item8)
session.commit()


print "added menu items!"
