from flask import Flask, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
import os

app = Flask(__name__)

load_dotenv()
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_USER = os.getenv('MONGODB_USER')

# connect to database
conn_str = ('mongodb+srv://'+MONGODB_USER+':'+MONGODB_PASSWORD+'@cluster0.2r2cif0.mongodb.net/?retryWrites=true&w=majority')
client = MongoClient(conn_str, connectTimeoutMS=30000, socketTimeoutMS=None, connect=False, maxPoolsize=1)
db = client['Kilimanjaro_VR']
coll = db['data']

@app.route('/')
def home():
    # Make a query to the specific DB and Collection
    cursor = coll.find({})
    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))
    # Delete the _id
    del df['_id']
    # convert epoch time to just the date
    df['date'] = pd.to_datetime(df['date'], unit='s').dt.date
    return render_template('home.html', df=df)

def week_summary():
    return

if __name__ == "__main__":
    app.run(debug=True)