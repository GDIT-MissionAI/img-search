import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from keras.preprocessing.image import load_img
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
    
    #returns PIL img
    pImg = readObject(sBucket, sKey)
    model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3), pooling='max')
    imgFeatures = extract_features(pImg, model)
    
    
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
    input_shape = (224, 224, 3)
    img =  load_img(bytesImg, target_size=(input_shape[0], input_shape[1]))
    return(img)

     #object = s3.Object(bucket_name,path)
     #img = load_img(io.BytesIO(object.get()['Body'].read()))
     #return(img)

def extract_features(img, model):
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    features = model.predict(preprocessed_img)
    flattened_features = features.flatten()
    normalized_features = flattened_features / norm(flattened_features)
    return normalized_features    
    
def Pickle(features):
    # convert document to vector of word embeddings
    print("Features")
    print(features)
    serialized_embedding = base64.b64encode(pickle.dumps(features, protocol=5))
    return serialized_embedding

def storeDynamoDB(SerializedContent):
    
    
    
