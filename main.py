import dash
import dash_core_components as dcc
import dash_html_components as html
import pymysql.cursors
import pandas as pd
import random
import threading
import time

conn = pymysql.connect(host='127.0.0.1',
                       user='root',
                       passwd='password',
                       db='trains',
                       cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

def db_query():
    query = ("SELECT * FROM train")
    cursor.execute(query)
    global df_rvp_stream
    df_rvp_stream = pd.read_sql("SELECT * FROM train", conn)
    pd.set_option('display.expand_frame_repr', False)
    df_rvp_stream.drop(['id'], inplace = True, axis = 1)
    df_rvp_stream.drop(['datedeparture'], inplace = True, axis = 1)
    df_rvp_stream['headnum'] = df_rvp_stream['headnum'].astype(int)
    df_rvp_stream = df_rvp_stream.loc[df_rvp_stream['headnum'] >= 0]
    df_rvp_stream['datearrival'] = df_rvp_stream['datearrival'].str[:19]
    df_rvp_stream = df_rvp_stream.drop(df_rvp_stream[df_rvp_stream.tcs == '[]'].index)
    df_rvp_stream = df_rvp_stream.drop_duplicates(['headnum'], keep='last')
    df_rvp_stream = df_rvp_stream.sort_values('route', kind='mergesort')

def generate_table(dataframe, max_rows=100):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def thread_function(name):
    print("Thread %s: starting", name)
    while i == 1:
        time.sleep(10)
        a = "['SLLTrackChain410', 'SLLTrackChain412b', 'SLLTrackChain412a', 'SLLTrackChain412', 'SLLTrackChain414a', 'SLLTrackChain414', 'SLLTrackChain416g']"
        r = random.randint(1, 27)
        b = "['SLLTrackChain" + str(r) + "']"
        df_rvp_stream['tcs'] = df_rvp_stream['tcs'].replace(a, b)
        print(df_rvp_stream)
    print("Thread %s: finishing", name)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

db_query()
i = 1

r = random.randint(1,27)
b = "['SLLTrackChain" + str(r) + "']"

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {'background': '#111111',
    'text': '#111111'}

app.layout = html.Div(children=[
    html.H4(children='РВП данные', style={'textAlign': 'center', 'color': colors['text']}),
    generate_table(df_rvp_stream)
])

x = threading.Thread(target=thread_function, args=(1,))
x.start()

if __name__ == '__main__':
    app.run_server(debug=True)
