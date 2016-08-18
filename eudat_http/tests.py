from cStringIO import StringIO
import json
import os
import requests
import shutil

from settings import STORAGE_DIR, md_store as md


base_url = "http://localhost:5000/"
objects_url = base_url + "digitalobjects"


def setup():
    shutil.rmtree(STORAGE_DIR)
    os.makedirs(STORAGE_DIR)
    md.clear_metadata()


def tearDown():
    shutil.rmtree(STORAGE_DIR)
    os.makedirs(STORAGE_DIR)
    md.clear_metadata()


def _create_object():
    r = requests.post(objects_url)
    assert r.status_code == 200
    response = r.json()
    return response['id']


def test_list_objects():
    r = requests.get(objects_url)
    assert r.status_code == 200
    assert r.json() == []


def test_create_object():
    object_id = _create_object()
    r = requests.get(objects_url)
    assert r.json() == [{'id' : object_id}]
    object_url = objects_url + "/" + object_id
    r = requests.get(object_url)
    assert r.status_code == 200
    assert r.json()['status'] == 'draft'


def test_change_status():
    object_id = _create_object()
    object_url = objects_url + '/' + object_id
    requests.patch(object_url, json={'status': 'committed'})
    r = requests.get(object_url)
    assert r.status_code == 200
    assert r.json()['status'] == 'committed'


def test_delete_object():
    object_id = _create_object()
    object_url = objects_url + "/" + object_id
    r = requests.delete(object_url)
    assert r.status_code == 204
    r = requests.get(object_url)
    assert r.status_code == 200
    assert r.json()['status'] == 'deleted'


def test_create_entity():
    object_id = _create_object()
    entity_url = objects_url + "/" + object_id + '/entities'
    files = {"file" : ('test.txt', 'Hello World!')}
    r = requests.post(entity_url,  files=files)
    assert r.status_code == 200
    response = r.json()
    assert 'id' in response
    entity_id = response['id']
    assert response['length'] == 12
    assert response['name'] == 'test.txt'
    assert response['checksum'] == '2ef7bde608ce5404e97d5f042f95f89f1c232871'
    r = requests.get(entity_url)
    assert r.status_code == 200
    assert r.json() == [{'id' : entity_id}]
    r = requests.get(entity_url + '/' + entity_id)
    assert r.status_code == 200
    assert r.text == 'Hello World!'


def test_create_objects_and_entities():
    object1_id = _create_object()
    object2_id = _create_object()
    entity1_url = objects_url + "/" + object1_id + '/entities'
    entity2_url = objects_url + "/" + object2_id + '/entities'
    files = {"file" : ('test.txt', 'Hello World!')}
    r = requests.post(entity1_url,  files=files)
    assert r.status_code == 200
    response = r.json()
    assert 'id' in response
    entity1_id = response['id']
    assert response['length'] == 12
    assert response['name'] == 'test.txt'
    assert response['checksum'] == '2ef7bde608ce5404e97d5f042f95f89f1c232871'
    r = requests.post(entity2_url,  files=files)
    entity2_id = r.json()['id']
    r = requests.get(entity1_url)
    assert r.status_code == 200
    assert r.json() == [{'id' : entity1_id}]
    r = requests.get(entity2_url)
    assert r.status_code == 200
    assert r.json() == [{'id' : entity2_id}]
    r = requests.get(entity1_url + '/' + entity1_id)
    assert r.status_code == 200
    assert r.text == 'Hello World!'
