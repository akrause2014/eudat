import os

STORAGE_DIR = '/tmp/data/'
METADATA_DIR = 'metadata'
DATA_DIR = 'data'

try:
    os.makedirs(STORAGE_DIR)
except:
    pass
