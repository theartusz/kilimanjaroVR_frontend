from flask import Flask, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField
import pandas as pd
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sh!'

load_dotenv()
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_USER = os.getenv('MONGODB_USER')

# connect to database
conn_str = ('mongodb+srv://'+MONGODB_USER+':'+MONGODB_PASSWORD+'@cluster0.2r2cif0.mongodb.net/?retryWrites=true&w=majority')
client = MongoClient(conn_str, connectTimeoutMS=30000, socketTimeoutMS=None, connect=False, maxPoolsize=1)
db = client['Kilimanjaro_VR']
coll = db['data']

activity_types = coll.distinct("activity_type")
activity_types.append('wszystko')

class FilterForm(FlaskForm):
    date_from = DateField('Date from', format="%d/%m/%Y")
    date_to = DateField('Date to', format="%d/%m/%Y")
    athlete_full_name = SelectField('Athlete name', choices=coll.distinct("athlete_full_name"))
    activity_type = SelectField('Activity type', choices=activity_types)
    submit = SubmitField('Filter')

def get_data(date_from=None, date_to=None, athlete_name=None, activity_type=None):
    # construct the query
    query = {}
    if date_from and date_to:
        query['date'] = {'$gte': date_from, '$lte': date_to}
    elif date_from:
        query['date'] = {'$gte': date_from}
    elif date_to:
        query['date'] = {'$lte': date_to}
    if athlete_name:
        query['athlete_full_name'] = athlete_name
    if activity_type != 'wszystko':
        query['activity_type'] = activity_type
    print(query)
    # construct the DataFrame
    df = pd.DataFrame(list(coll.find(query)))
    # Delete the _id and transform data first time dataframe is loaded
    if '_id' in df:
        del df['_id']
        # convert epoch time to just the date
        df['datetime'] = pd.to_datetime(df['date'], unit='s')
        df['date'] = pd.to_datetime(df['datetime'], unit='s').dt.date
        df['week_nr'] = df['datetime'].dt.isocalendar().week
    return df

@app.route('/', methods=['post','get'])
def home():
    form = FilterForm(activity_type='wszystko')
    df = get_data(
        date_from=form.date_from.data,
        date_to=form.date_to.data,
        athlete_name=form.athlete_full_name.data,
        activity_type=form.activity_type.data
    )
    print(form.date_from.data)
    return render_template('home.html', df=df, form=form)

@app.route('/week')
def week_summary():
    df = get_data()
    weekly_summary = df.groupby(by=['week_nr']).sum()
    print(weekly_summary)
    return render_template('home.html', df=df)

if __name__ == "__main__":
    app.run(port=5000)