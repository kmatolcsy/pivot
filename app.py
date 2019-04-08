import os
import threading
import webbrowser as wb
import datetime as dt
import pandas as pd
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc

from flask import Flask, render_template
from dash.dependencies import Input, Output


class Directory:
    def __init__(self, path):
        self.path = path
        self.path_list = path.split('/')
        self.data_ext = ['.csv', 'xls', '.xlsx']

    def is_data(self, file_name):
        _, ext = os.path.splitext(file_name)
        return ext in self.data_ext

    def list_dirs(self):
        return [entry for entry in os.scandir(self.path) if entry.is_dir()]

    def list_files(self):
        return [entry for entry in os.scandir(self.path) if entry.is_file() and self.is_data(entry.name)]


# flask server / file explorer
server = Flask(__name__)
# dash application
app = dash.Dash(__name__, server=server, assets_folder='static', url_base_pathname='/dash_base/')
app.layout = html.Div('initial layout')
app.config['suppress_callback_exceptions'] = True
# working dir
os.chdir(os.path.expanduser('~'))


def read_data(path, *kwargs):
    _, ext = os.path.splitext(path)

    if ext == '.csv':
        df = pd.read_csv(path, *kwargs)
    else:
        df = pd.read_excel(path, *kwargs)

    return df


def layout(path):
    df = read_data(path)
    dd_options = [{'label': col, 'value': col} for col in df.columns.values]

    return html.Div(
        id='layout',
        className='container',
        children=[
            html.Button(
                id='path',
                className='btn btn-secondary',
                children='btn',
                type='button',
                title=path,
                **{'data-toggle': 'tooltip', 'data-placement': 'left'}
            ),
            dcc.Dropdown(
                id='x-axis',
                options=dd_options,
                value=dd_options[0]['value']
            ),
            dcc.Dropdown(
                id='y-axis',
                options=dd_options,
                multi=True,
                value=dd_options[-1]['value']
            ),
            html.Div(
                id='graph'
            )
        ]
    )


@app.callback(
    Output('graph', 'children'),
    [Input('x-axis', 'value'), Input('y-axis', 'value'), Input('path', 'title')])
def graph(idx, columns, path):
    print(idx)
    df = read_data(path)
    columns = [columns] if isinstance(columns, str) else columns

    return dcc.Graph(
        figure={
            'data': [{'x': df[idx], 'y': df[column], 'type': 'line', 'name': column} for column in columns],
            'layout': {'title': 'Dash Data Visualization'}
        }
    )


@server.template_filter('as_uri')
def as_uri(path):
    return path.replace(os.sep, '/')


@server.template_filter('as_date')
def as_date(seconds):
    return dt.datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M')


@server.route('/', defaults={'path': '.'})
@server.route('/<path:path>')
def index(path):
    current_dir = Directory(path)
    return render_template('index.html', current_dir=current_dir)


@server.route('/plot/<path:path>')
def plot(path):
    app.layout = layout(path)
    return app.index()


# t = threading.Thread(target=server.run)
# t.start()
# wb.open_new('http://localhost:5000/')

if __name__ == '__main__':
    server.run(debug=True)

