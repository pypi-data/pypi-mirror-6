import pymongo
from bson.objectid import ObjectId
from django.conf import settings
from cloudengine.classes.utils import validate_db_name


class ClassesManager(object):
    client = pymongo.MongoClient(settings.MONGO_HOST)
    
    def get_classes(self, db):
        db = validate_db_name(db)
        db = self.client[db]
        collections = db.collection_names(include_system_collections=False)
        app_classes = []
        for coll in collections:
            doc = db[coll].find_one()
            if doc: app_classes.append(coll)
        return app_classes
    
    
    def get_class(self, db, klass, query, sort_key=None, direction = None):
        db = validate_db_name(db)
        try:
            if direction:
                assert(direction == pymongo.ASCENDING or direction == pymongo.DESCENDING)
        except AssertionError:
            raise Exception("valid values for order are 1 & -1")
        
        db = self.client[db]
        collection = db[klass]
        cursor = collection.find(query)      
        if sort_key:
            cursor = cursor.sort(sort_key, direction)
            
        res = [doc for doc in cursor]

        for doc in res:
            objid = doc["_id"]
            doc["_id"] = str(objid)
        return res
    
    
    def delete_class(self, db, klass):
        db = validate_db_name(db)
        db = self.client[db]
        if klass in db.collection_names():
            db.drop_collection(klass)


    def add_object(self, db, klass, obj):
        db = validate_db_name(db)
        db = self.client[db]
        collection = db[klass]
        keys = obj.keys()
        if ("_id" in keys):
            raise Exception("Invalid object. _id is a reserved field")
        
        objid = collection.insert(obj)
        return objid
    
    
    def add_multiple_objects(self, db, klass, objects):
        db = validate_db_name(db)
        db = self.client[db]
        collection = db[klass]
        for obj in objects:
            keys = obj.keys()
            if ("_id" in keys):
                raise Exception("Invalid object. _id is a reserved field")
        ids = collection.insert(objects)
        return ids
        
        
    def get_object(self, db, klass, id):
        db = validate_db_name(db)
        db = self.client[db]
        collection = db[klass]
        query = {"_id": ObjectId(id)}
        obj = collection.find_one( query)
        if obj:
            objid = obj["_id"]
            obj["_id"] = str(objid)
        return obj
        
        
    def update_object(self, db, klass, id, obj):
        db = validate_db_name(db)
        db = self.client[db]
        collection = db[klass]
        updates = obj.keys()
        if ("_id" in updates):
            raise Exception("Invalid object. _id is a reserved field")
        collection.update({"_id": ObjectId(id)},
                          {"$set": obj})               # todo: set multi = true??
        
        
    def delete_object(self, db, klass, id):
        db = validate_db_name(db)
        db = self.client[db]
        collection = db[klass]
        collection.remove(ObjectId(id))
        if not collection.count():
            db.drop_collection(klass)
        
    def delete_app_data(self, db):
        db = validate_db_name(db)
        db = self.client[db]
        collections = db.collection_names(include_system_collections=False)
        for collection in collections:
            col = db[collection]
            col.remove()
