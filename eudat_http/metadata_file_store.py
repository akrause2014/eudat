import json
import os
from settings import STORAGE_DIR, METADATA_DIR


def create_object(object_id):
    try:
        os.makedirs(get_md_dir(object_id))
    except:
        import traceback
        print(traceback.format_exc())


def get_status(object_id):
    md_dir = get_md_dir(object_id)
    with open(os.path.join(md_dir, 'status')) as f:
        return f.read()


def set_status(object_id, status):
    md_dir = get_md_dir(object_id)
    with open(os.path.join(md_dir, 'status'), 'w') as f:
        return f.write(status)


def store_metadata(object_id, metadata):
    md_dir = get_md_dir(object_id)
    with open(os.path.join(md_dir, 'metadata'), 'w') as f:
       json.dump(metadata, f)


def get_metadata(object_id):
    with open(os.path.join(get_md_dir(object_id), 'metadata')) as f:
        metadata = json.load(f)


def store_entity_metadata(object_id, entity_id, entity_md):
    md_path = os.path.join(get_md_dir(object_id), "metadata_" + entity_id)
    with open(md_path, 'w') as f:
        json.dump(entity_md, f)


def get_md_dir(object_id):
    object_dir = os.path.join(STORAGE_DIR, object_id)
    return os.path.join(object_dir, METADATA_DIR)
