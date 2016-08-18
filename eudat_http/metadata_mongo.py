from pymongo import MongoClient
from settings import MONGODATABASENAME, STATUS_DRAFT


# stores objects in collection "objects"
# stores entities in collection "entities"

def clear_metadata():
    # clear the collections - for testing purposes only!
    client = MongoClient()
    db = client[MONGODATABASENAME]
    db.objects.delete_many({})
    db.entities.delete_many({})

# return a list of all the object ids in the database
def list_objects():
    client = MongoClient()
    db = client[MONGODATABASENAME]
    objects = db.objects.find()
    return objects

def create_object(object_id):
    db = MongoClient()[MONGODATABASENAME]
    db.objects.insert_one(
        {'object_id': object_id,
         'metadata': None,
         'status': STATUS_DRAFT})

# store metadata for an object
# if the object already exists then the metadata will be updated,
# otherwise a new object will be created.
def store_metadata(object_id, metadata):
    client = MongoClient()
    db = client[MONGODATABASENAME]
    db.objects.update(
        {'object_id': object_id},
        {'object_id': object_id, 'metadata': metadata, 'status': STATUS_DRAFT},
        upsert=True
    )        


# get an object's metadata, or None if the object does not exist
def get_metadata(object_id):
    document = get_object(object_id)
    if document == None:
        return None
    return document['metadata']

# get an object's status
def get_status(object_id):
    document = get_object(object_id)
    if document == None:
        return None
    return document['status']

# get everything that the database knows about the object
def get_object(object_id):
    client = MongoClient()
    db = client[MONGODATABASENAME]
    return db.objects.find_one({'object_id': object_id})

# set the object status
def set_status(object_id, status):
    payload = { "status": status }
    __update_document(object_id, payload)


# update an existing object
# payload is a dict containing the fields and values to update
def __update_document(object_id, payload):
    client = MongoClient()
    db = client[MONGODATABASENAME]
    result = db.objects.update_one(
        {"object_id": object_id},
        {
            "$set": payload,
            "$currentDate": {"lastModified": True}
        })
    return result.modified_count


# add or update an entity
def update_entity(entity_id, filename):
    client = MongoClient()
    db = client[MONGODATABASENAME]
    
    result = db.entities.update_one(
        {'entity_id': entity_id},
        {
            "$set": {'filename': filename},
            "$setOnInsert": {'entity_id': entity_id, 'filename': filename},
            "$currentDate": {"lastModified": True}
        },
        upsert=True)

# get information about an entity
def get_entity(entity_id):
    client = MongoClient()
    db = client[MONGODATABASENAME]

     # look for an existing entity
    document = db.entities.find_one({'entity_id': entity_id})
    return document


def store_entity_metadata(object_id, entity_id, entity_md):
    db = MongoClient()[MONGODATABASENAME]
    db.entities.update_one(
        {"entity_id": entity_id},
        {
           "$set": { 'metadata': entity_md},
           "$currentDate": {"lastModified": True}
        },
        upsert=True
    )

# delete an entity
def delete_entity(entity_id):
     client = MongoClient()
     db = client[MONGODATABASENAME]
     db.entities.delete_one( {'entity_id': entity_id})




