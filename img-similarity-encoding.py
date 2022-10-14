import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from nltk import sent_tokenize
import pickle
from sentence_transformers import SentenceTransformer
import json
import boto3
import botocore
import base64
from base64 import b64encode
import os
os.environ['TRANSFORMERS_CACHE'] = '/tmp'

#load clients
s3Client = boto3.client('s3')

#load pipeline
model = SentenceTransformer('model/')

#load clients
s3Client = boto3.client('s3')

# Takes any "Context" given as input and vectorizes it.
# The routine here is a central place where vectorization routines for search & content can be centrally adjusted. Results are often presisted,
# so content will typically need to be reprocessed to get latest vectors should the vector routine or content change.
def lambda_handler(event, context):
    print(json.dumps(event))
    sContext = event.get("Context")
    print(sContext)
    
#    if (sContext == ""):
#        sBucket = event.get("Bucket")
#        sKey = event.get("Key")
#        sContext = readObject(sBucket, sKey)
        
    if (sContext != ""):
        bVector = Vectorize(sContext)
        print(type(bVector))
        print(bVector)
        sVector = str(bVector)
        print(type(sVector))
        print(sVector)
        sVector =  sVector.strip("\"")
        print(sVector)
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'body': sVector #return answers to caller
    }
    
#Read from S3
def readObject(sBucket, sKey):
  return s3Client.get_object(Bucket=sBucket, Key=sKey)['Body'].read().decode('utf-8')

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
