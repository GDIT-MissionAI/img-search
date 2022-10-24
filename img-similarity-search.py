

import numpy as np
from numpy.linalg import norm
#from tqdm import tqdm, tqdm_notebook
import os
import time
import pickle
import json
from json import JSONEncoder
import boto3
import botocore
import base64
from base64 import b64encode
import urllib.parse
from datetime import datetime
from io import BytesIO
from io import StringIO

#load environment variables
os.environ["CUDA_VISIBLE_DEVICES"]="-1" #only allow tensorflow to run on CPU. Waiting for a GPU enabled Lambda.
os.environ["TFHUB_CACHE_DIR"]="/model" 
sEventBusName = os.environ['EventBus_Name']
sImageFeaturesTableName = os.environ['ImageFeaturesTable']

#load clients
s3Client = boto3.client('s3')
dbResource = boto3.resource('dynamodb')
clientEvents = boto3.client('events')


# Takes any "Context" given as input and vectorizes it.
# The routine here is a central place where vectorization routines for search & content can be centrally adjusted. Results are often presisted,
# so content will typically need to be reprocessed to get latest vectors should the vector routine or content change.
def lambda_handler(event, context):
    print(json.dumps(event))
