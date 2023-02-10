from flask import Flask, render_template
from pymongo import MongoClient
import os
import pandas as pd

app = Flask(__name__)

MONGODB_PASSWORD = os.environ['MONGODB_PASSWORD']
MONGODB_USER = os.environ['MONGODB_USER']

# connect to database
conn_str = ('mongodb+srv://'+MONGODB_USER+':'+MONGODB_PASSWORD+'@cluster0.2r2cif0.mongodb.net/?retryWrites=true&w=majority')
client = MongoClient(conn_str, connectTimeoutMS=30000, socketTimeoutMS=None, connect=False, maxPoolsize=1)
db = client['Kilimanjaro_VR']
coll = db['data']

# Make a query to the specific DB and Collection
cursor = coll.find({})
# Expand the cursor and construct the DataFrame
df =  pd.DataFrame(list(cursor))
# Delete the _id
del df['_id']

@app.route('/')
def hello():
    return render_template('home.html', df=df)