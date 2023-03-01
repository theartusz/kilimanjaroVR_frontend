from flask import Flask, render_template
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

class FilterForm(FlaskForm):
    date_from = DateField('Od', format="%Y-%m-%d")
    date_to = DateField('Do', format="%Y-%m-%d")
    athlete_full_name = SelectField('Imie sportowca')
    activity_type = SelectField('Aktivita', choices=['bieg', 'kolo', 'biezki', 'plywani', 'wszystko'])
    submit = SubmitField('Filtruj')

def get_data(date_from=None, date_to=None, athlete_name=None, activity_type=None):
    # convert date to int and add 1 day to date_to
    if date_from:
        date_from = int(date_from.strftime('%s'))
    if date_to:
        date_to = int(date_to.strftime('%s')) + 86400
    # construct the query
    query = {}
    if date_from and date_to:
        query['date'] = {'$gte': date_from, '$lte': date_to}
    elif date_from:
        query['date'] = {'$gte': date_from}
    elif date_to:
        query['date'] = {'$lte': date_to}
    if athlete_name != 'wszyscy':
        query['athlete_full_name'] = athlete_name
    if activity_type != 'wszystko':
        query['activity_type'] = activity_type
    # construct the DataFrame
    df = pd.DataFrame(list(coll.find(query)))
    # Delete the _id and transform data first time dataframe is loaded
    if '_id' in df:
        del df['_id']
        # convert epoch time to just the date
        df['datetime'] = pd.to_datetime(df['date'], unit='s')
        #df['week_nr'] = df['datetime'].dt.isocalendar().week
    return df

@app.route('/data', methods=['post','get'])
def data():
    # create list with names of all athletes
    athlete_full_names = coll.distinct("athlete_full_name")
    athlete_full_names.append("wszyscy")
    # invoke form and select default choices
    form = FilterForm(athlete_full_name='wszyscy', activity_type='wszystko')
    form.athlete_full_name.choices = athlete_full_names

    df = get_data(
        date_from=form.date_from.data,
        date_to=form.date_to.data,
        athlete_name=form.athlete_full_name.data,
        activity_type=form.activity_type.data
    )
    df['date'] = pd.to_datetime(df['datetime'], unit='s').dt.date
    return render_template('data.html', df=df, form=form)

@app.route('/')
def week_summary():
    df = get_data(
        date_from=None,
        date_to=None,
        athlete_name="wszyscy",
        activity_type="wszystko"
        )
    # add week_start column
    df['week_start'] =  df['datetime'].dt.to_period('W').dt.start_time
    # Set the date column as the index
    df = df.set_index('datetime')
    # Pivot the table to get the distances for each day of the week
    pivot_table = pd.pivot_table(df, index=['athlete_full_name', 'week_start'], columns=[df.index.day_name()], values='recalculated_distance', aggfunc=sum, fill_value=0)
    pivot_table = pivot_table.reset_index()
    # calculate weekly total kilometers per person
    pivot_table['weekly_total'] = pivot_table.iloc[:, 2:].select_dtypes(include='number').sum(axis=1)
    # add column with year and week number
    pivot_table['Year-Week'] = pivot_table['week_start'].dt.strftime('%Y-%U')
    # sort tables
    pivot_table = pivot_table.sort_values(by=['week_start'])

    weeks = pivot_table['Year-Week'].unique().tolist()

    return render_template('week.html', df=pivot_table, weeks=weeks)

if __name__ == "__main__":
    app.run(port=5000)