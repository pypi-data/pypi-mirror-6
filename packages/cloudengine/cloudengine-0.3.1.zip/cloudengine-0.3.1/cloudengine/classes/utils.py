from pymongo import MongoClient
from django.conf import settings



# Mongo db names cannot have . in their names
def validate_db_name(db_name):
    db_name = db_name.replace('.', '__')
    return db_name
