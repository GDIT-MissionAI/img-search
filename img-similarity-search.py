from sklearn.neighbors import NearestNeighbors
import os
import time
import pickle
import json
from json import JSONEncoder
import boto3
import botocore
import base64
from base64 import b64encode
from datetime import datetime


#load environment variables
sEventBusName = os.environ['EventBus_Name']
sImageFeaturesTableName = os.environ['ImageFeaturesTable']

#load clients
dbResource = boto3.resource('dynamodb')

def lambda_handler(event, context):
    print(json.dumps(event))
    
    #Search Logic
    feature_list = []
    img_list = []
    
    dsImgFeatures = retrievePickles(sImageFeaturesTableName)

    for row in dsImgFeatures:
        feature_list.append(DeVectorize(row["Pickle"]))
        img_list.append(row["AssetId"])

    neighbors = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='euclidean').fit(feature_list)

    scores_dump = base64.b64encode(pickle.dumps(feature_list))
    img_dump = base64.b64encode(pickle.dumps(img_list))
    
    random_index = 75
    distances, indices = neighbors.kneighbors([feature_list[random_index]])
    
    #return the content.
    return {
        'statusCode': 200,
        'scores' : scores_dump,
        'images' : img_dump,
        'body': json.dumps('Pickles have been created!')
    }

#Determine Probabilities
def generateComparison(dsImgFeatures):
    #loop over retrieved pickles
    

#Retrieve Pickles
def retrievePickles(sTableName):
    table = dbResource.Table(sTableName)
    response = table.scan()
    data = response.get('Items')
    while 'LastEvaluatedKey' in response:
        #response = kwargs.get('table').scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    print("pickles list")
    print(data)
    return data

def DeVectorize(sContent):
    # convert document to vector of word embeddings
    print("Decode")
    #print(sContent)
    #print(base64.b64decode(sContent))
    #serialized_embedding = pickle.loads(base64.b64decode(sContent))
    print(sContent)
    print(type(sContent))
    print(base64.b64decode(sContent))
    print(type(base64.b64decode(sContent)))
    
    #serialized_embedding = pickle.loads(base64.b64decode(sContent))
#    serialized_embedding = pickle.loads(sContent)

    sContent = sContent[2:len(sContent)-1]
    print(sContent)
    sContent2 = bytes(sContent, 'utf-8')
    print(sContent2)
    sContent3 = base64.b64decode(sContent)
    print("decoded")
    print(sContent3)
    print("pickle load")
    serialized_embedding = pickle.loads(sContent3)
    print(serialized_embedding)
    
    return serialized_embedding
