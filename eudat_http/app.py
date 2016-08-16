'''
curl http://127.0.0.1:5000/digitalobjects/
curl http://127.0.0.1:5000/digitalobjects/ed2c0631-6ccf-42ea-9ae0-e0fe93327847/entities
curl -X POST --form "file=@/tmp/test.txt" http://127.0.0.1:5000/digitalobjects/ed2c0631-6ccf-42ea-9ae0-e0fe93327847/entities
'''

import os
import uuid
import json

from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
from settings import STORAGE_DIR, METADATA_DIR, DATA_DIR
import digital_objects as d

STATUS_DRAFT = 'draft'
STATUS_COMMITTED = 'committed'
STATUS_PUBLISHED = 'published'
STATUS_DELETED = 'deleted'

app = Flask(__name__)
api = Api(app)

class DigitalObjects(Resource):
    def get(self):
        result = []
        for p in d.list_dirs(STORAGE_DIR):
            result.append({"id": p})
        return result

    def post(self):
        object_id = d.create_digital_object()
        object_dir = os.path.join(STORAGE_DIR, object_id)
        md_dir = os.path.join(object_dir, METADATA_DIR)
        metadata = request.get_json()
        if not metadata:
            metadata = {}
        status = STATUS_DRAFT
        with open(os.path.join(md_dir, 'metadata'), 'w') as f:
           json.dump(metadata, f)
        with open(os.path.join(md_dir, 'status'), 'w') as f:
           f.write(status)
        return {"id": object_id}


class DigitalObject(Resource):

    def get(self, object_id):
        with open(os.path.join(d.get_md_dir(object_id), 'metadata')) as f:
            metadata = json.load(f)
        status = d.get_status(object_id)
        return {"id": object_id, 
                "metadata": metadata, 
                "status": status,
                "files_count": d.count_files(d.get_data_dir(object_id))}

    def patch(self, object_id):
        body = request.get_json()
        if body is None or 'status' not in body:
            return {'message' : 'Invalid request: Status expected.'}, 400
        new_status = body['status']
        md_dir = d.get_md_dir(object_id)
        with open(os.path.join(md_dir, 'status'), 'w') as f:
           f.write(new_status)
        return {"id": object_id, "status": new_status}

    def delete(self, object_id):
        status = d.get_status(object_id)
        if status == STATUS_DRAFT:
            d.set_status(object_id, STATUS_DELETED)
            return '', 204
        else:
            return {'message': 'Digital object is not in draft status'}, 405



class DigitalEntities(Resource):

    def get(self, object_id):
        result = []
        for p in d.list_files(d.get_data_dir(object_id)):
            result.append({"id": p})
        return result

    def post(self, object_id):
        datafile = request.files['file']
        file_name = datafile.filename
        entity_id = str(uuid.uuid4())
        # entity_id = file_name
        entity_path = os.path.join(d.get_data_dir(object_id), entity_id)
        datafile.save(entity_path)
        file_length = os.path.getsize(entity_path)
        file_hash = d.get_checksum(entity_path)
        md_path = os.path.join(d.get_md_dir(object_id), "metadata_" + entity_id)
        entity_md =  {"id": entity_id, 
                      "name": file_name,
                      "length": file_length, 
                      "checksum": file_hash}
        with open(md_path, 'w') as f:
            json.dump(entity_md, f)
        return entity_md


class DigitalEntity(Resource):

    def get(self, object_id, entity_id):
        return send_from_directory(directory=d.get_data_dir(object_id), filename=entity_id)

    def delete(self, object_id, entity_id):
        os.remove(os.path.join(d.get_data_dir(object_id), entity_id))
        return '', 204


api.add_resource(DigitalObjects, '/digitalobjects')
api.add_resource(DigitalObject, '/digitalobjects/<object_id>')
api.add_resource(DigitalEntities, '/digitalobjects/<object_id>/entities')
api.add_resource(DigitalEntity, '/digitalobjects/<object_id>/entities/<entity_id>')


if __name__ == '__main__':
    app.config.from_object('settings')
    app.run(debug=True)