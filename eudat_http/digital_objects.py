import os
import uuid
import hashlib

from settings import STORAGE_DIR, DATA_DIR
import metadata_file_store as md

def create_digital_object():
    for i in range(10): # try up to 10 times to create an id
        object_uid = uuid.uuid4()
        object_id = str(object_uid)
        object_dir = os.path.join(STORAGE_DIR, object_id)
        try:
            os.makedirs(object_dir)
            os.makedirs(os.path.join(object_dir, DATA_DIR))
            md.create_object(object_id)
            return object_id
        except:
            import traceback
            print(traceback.format_exc())
            # if the directory exists or can't be created we try again
            pass


def create_entity(object_id, entity_id, datafile):
    file_name = datafile.filename
    entity_path = os.path.join(get_data_dir(object_id), entity_id)
    datafile.save(entity_path)
    file_length = os.path.getsize(entity_path)
    file_hash = get_checksum(entity_path)
    entity_md =  {"id": entity_id, 
                  "name": file_name,
                  "length": file_length, 
                  "checksum": file_hash}
    md.store_entity_metadata(object_id, entity_id, entity_md)
    return entity_md


def list_objects():
    result = [{"id": p} for p in list_dirs(STORAGE_DIR)]
    return result

def count_entities(object_id):
    return count_files(get_data_dir(object_id))


def list_entities(object_id):
    return list_files(get_data_dir(object_id))



def get_obj_dir(object_id):
    return os.path.join(STORAGE_DIR, object_id)
    
def get_data_dir(object_id):
    return os.path.join(get_obj_dir(object_id), DATA_DIR)

def list_dirs(a_dir):
    for name in os.listdir(a_dir):
        if os.path.isdir(os.path.join(a_dir, name)):
            yield name

def list_files(a_dir):
    for name in os.listdir(a_dir):
        if os.path.isfile(os.path.join(a_dir, name)):
            yield name

def count_files(a_dir):
    return len([1 for name in os.listdir(a_dir) \
                if os.path.isfile(os.path.join(a_dir, name))])


def get_checksum(file_name):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(file_name, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


