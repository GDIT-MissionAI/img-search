import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
import numpy
from numpy.linalg import norm
from tqdm import tqdm, tqdm_notebook
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

#load clients
s3Client = boto3.client('s3')


# Takes any "Context" given as input and vectorizes it.
# The routine here is a central place where vectorization routines for search & content can be centrally adjusted. Results are often presisted,
# so content will typically need to be reprocessed to get latest vectors should the vector routine or content change.
def lambda_handler(event, context):
    print(json.dumps(event))
    
    sBucket = event.get("Bucket")
    sKey = event.get("Key")
    sContext = readObject(sBucket, sKey)
    
    
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'body': sVector #return answers to caller
    }
    
#Read from S3
def readObject(sBucket, sKey):
    byteString = s3Client.get_object(Bucket=sBucket, Key=sKey)['Body'].read() #grab the s3 object.
    bytesImg = BytesIO(byteString) #pull bytes
    tmppilImage = Image.open(bytesImg) #get me an image from the bytes.

def Vectorize(sContent):
    # convert document to vector of word embeddings
    sentences = sent_tokenize(sContent)
#    print("1")
#    print(sentences)
    base_embeddings_sentences = model.encode(sentences)
#    print("2")
#    print(base_embeddings_sentences)
    base_embeddings = np.mean(np.array(base_embeddings_sentences), axis=0)
#    print("3")
#    print(base_embeddings)
#    serialized_embedding = pickle.dumps(base_embeddings) #prior code
    serialized_embedding = base64.b64encode(pickle.dumps(base_embeddings, protocol=5))
    return serialized_embedding
