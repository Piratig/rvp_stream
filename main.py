import time
import dash
import pymysql.cursors
from dash import Input, Output, callback
from dash import dash_table as dt
from dash import dcc
from dash import html
import pandas as pd

# DB connect
conn = pymysql.connect(host='127.0.0.1',
                       user='root',
                       passwd='password',
                       db='trains',
                       cursorclass=pymysql.cursors.DictCursor)


# Filtering DataFrame by line name
def df_update(line_name, df):
    df = df.loc[df['line'] == "{0}".format(line_name)]
    df = df.drop_duplicates(['route'], keep='first') # When the request changes, change to the keep='first'
    df = df.sort_values('route', kind='mergesort')
    return df

# Loading data from DB into DataFrame
def db_query():
    cursor = conn.cursor()
    df_rvp_query = pd.read_sql("SELECT line, route, headnum, tcs, datearrival FROM train ORDER BY id DESC LIMIT 1000", conn)
    pd.set_option('display.expand_frame_repr', False)
    df_rvp_query['headnum'] = df_rvp_query['headnum'].astype(int)
    df_rvp_query = df_rvp_query.loc[df_rvp_query['headnum'] >= 0]
    df_rvp_query['datearrival'] = df_rvp_query['datearrival'].str[:19]
    df_rvp_query = df_rvp_query.drop(df_rvp_query[df_rvp_query.tcs == '[]'].index)
    conn.commit()
    return df_rvp_query

# Initialization
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
global df_rvp_stream
df_rvp_stream = db_query()
df_rvp_stream = df_update('', df_rvp_stream)

# Creating a web page with Dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(children=[
    html.H4(children='РВП данные', style={'textAlign': 'center', 'color': '#111111'}),
    dcc.Dropdown(id = 'dpd',
                 options=[
                     {'label': 'SLL', 'value': 'sllLine'},
                     {'label': 'NKL', 'value': 'nklLine'}
                 ],
                 value='sllLine'
                 ),
    dt.DataTable(id='tbl', style_data={'whiteSpace': 'normal', 'height': 'auto', },
                 data=df_rvp_stream.to_dict('records'),
                 columns=[{"name": i, "id": i} for i in df_rvp_stream.columns],
                 style_cell = {'textAlign': 'left'},
                 ),
    dcc.Interval(id='time',
                 interval=5 * 1000,
                 n_intervals=0),
])

@callback(Output('tbl', 'data'), [Input('time', 'n_intervals'), Input('dpd', 'value')])
def update_graphs(n_intervals, value):
    df_rvp_stream = db_query()
    df_rvp_stream = df_update(value, df_rvp_stream)
    new_df = df_rvp_stream.to_dict('records')
    print('Table updated')
    return new_df


if __name__ == '__main__':
    app.run_server(debug=True)
