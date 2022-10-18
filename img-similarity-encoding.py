import PIL
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.utils import load_img
import numpy as np
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

#load environment variables
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
    
    sAssetId = event["detail"]["AssetId"]
    sBucket = event["detail"]["AssetStorageBucket"]
    sKey = event["detail"]["AssetStorageKey"]
    
    #use if we make this independently invokable.
    #event.get("Bucket")
    #event.get("Key")
    
    #returns PIL img
    pImg = readObject(sBucket, sKey)
    model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3), pooling='max')
    imgFeatures = extract_features(pImg, model) #pull features
    sPickle = featurePickle(imgFeatures) #pickle features
    dbResponse = storeDynamoDB(sAssetId, sPickle, sImageFeaturesTableName) #write to db
    msgResponse = enrichmentEvent(sAssetId, sPickle) #record message
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps('Processed Image Features!')
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
    #img_array = Image.img_to_array(img)
    img_array = np.array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    features = model.predict(preprocessed_img)
    flattened_features = features.flatten()
    normalized_features = flattened_features / norm(flattened_features)
    return normalized_features    
    
def featurePickle(features):
    # convert document to vector of word embeddings
    print("Features")
    print(features)
    serialized_embedding = base64.b64encode(pickle.dumps(features, protocol=5))
    return serialized_embedding

def storeDynamoDB(sAssetId, SerializedContent, sImageFeaturesTableName):
    table = dbResource.Table(sImageFeaturesTableName)
    responseDynamoDB = table.put_item(
        Item={
            "AssetId": sAssetId,
            "Pickled": SerializedContent
        }
        )
    return responseDynamoDB

class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime)):
                return obj.isoformat()

#Write the event to the event bridge. It will kickoff other.
def enrichmentEvent(sAssetId, SerializedContent):
    print("Pickle")
    print(SerializedContent)
    print(type(SerializedContent))
    appEvent = {
        "AssetId": sAssetId,
        "Pickle": SerializedContent
    }
    
    bridgeEvent = {
        'EventBusName':sEventBusName,
        'Time': datetime.utcnow(),
        'Source':'gdit.missionai',
        'Resources' : [],
        'DetailType':'ImageFeatures',
        'Detail': json.dumps(appEvent, indent=4, cls=DateTimeEncoder)
    }
    
    # Send event to EventBridge
    responseEventPublish = clientEvents.put_events(
        Entries=[
            bridgeEvent
            ]
    )
    print(json.dumps(bridgeEvent, indent=4, cls=DateTimeEncoder))
#    print(responseEventPublish)
    return responseEventPublish #allow caller to determine whether to use response id or not.
