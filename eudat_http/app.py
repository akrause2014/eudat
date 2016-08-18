'''
curl http://127.0.0.1:5000/digitalobjects/
curl http://127.0.0.1:5000/digitalobjects/ed2c0631-6ccf-42ea-9ae0-e0fe93327847/entities
curl -X POST --form "file=@/tmp/test.txt" http://127.0.0.1:5000/digitalobjects/ed2c0631-6ccf-42ea-9ae0-e0fe93327847/entities
'''

import os
import uuid

from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
import digital_objects as d
from settings import md_store as md, STATUS_DRAFT, STATUS_DELETED


app = Flask(__name__)
api = Api(app)

class DigitalObjects(Resource):

    def get(self):
        return d.list_objects()

    def post(self):
        object_id = d.create_digital_object()
        metadata = request.get_json()
        if not metadata:
            metadata = {}
        md.store_metadata(object_id, metadata)
        md.set_status(object_id, STATUS_DRAFT)
        return {"id": object_id}


class DigitalObject(Resource):

    def get(self, object_id):
        metadata = md.get_metadata(object_id)
        status = md.get_status(object_id)
        return {"id": object_id, 
                "metadata": metadata, 
                "status": status,
                "files_count": d.count_entities(object_id)}

    def patch(self, object_id):
        body = request.get_json()
        if body is None or 'status' not in body:
            return {'message' : 'Invalid request: Status expected.'}, 400
        new_status = body['status']
        md.set_status(object_id, new_status)
        return {"id": object_id, "status": new_status}

    def delete(self, object_id):
        status = md.get_status(object_id)
        if status == STATUS_DRAFT:
            md.set_status(object_id, STATUS_DELETED)
            return '', 204
        else:
            return {'message': 'Digital object is not in draft status'}, 405



class DigitalEntities(Resource):

    def get(self, object_id):
        result = []
        for p in d.list_entities(object_id):
            result.append({"id": p})
        return result

    def post(self, object_id):
        datafile = request.files['file']
        entity_id = str(uuid.uuid4())
        # entity_id = file_name
        return d.create_entity(object_id, entity_id, datafile)


class DigitalEntity(Resource):

    def get(self, object_id, entity_id):
        return send_from_directory(directory=d.get_data_dir(object_id), filename=entity_id)

    def delete(self, object_id, entity_id):
        try:
            os.remove(os.path.join(d.get_data_dir(object_id), entity_id))
            md.delete_entity(object_id, entity_id)
            return '', 204
        except:
            return '', 404


api.add_resource(DigitalObjects, '/digitalobjects')
api.add_resource(DigitalObject, '/digitalobjects/<object_id>')
api.add_resource(DigitalEntities, '/digitalobjects/<object_id>/entities')
api.add_resource(DigitalEntity, '/digitalobjects/<object_id>/entities/<entity_id>')


if __name__ == '__main__':
    app.config.from_object('settings')
    app.run(debug=True)