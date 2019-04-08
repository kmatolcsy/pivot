import os
import threading
import webbrowser as wb
import datetime as dt
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc

from flask import Flask, render_template


class Directory:
    def __init__(self, path):
        self.path = path
        self.path_list = path.split('/')

        self.data_ext = ['.csv', '.xlsx']

    def is_data(self, file_name):
        _, ext = os.path.splitext(file_name)
        return ext in self.data_ext

    def list_dirs(self):
        return [entry for entry in os.scandir(self.path) if entry.is_dir()]

    def list_files(self):
        return [entry for entry in os.scandir(self.path) if entry.is_file() and self.is_data(entry.name)]


server = Flask(__name__)
app = dash.Dash(__name__, server=server, assets_folder='static', url_base_pathname='/dash_base/')
app.layout = html.Div('initial layout')
os.chdir(os.path.expanduser('~'))


def layout(path):
    df = pd.read_csv(path, index_col=0)
    return html.Div(
        className='container',
        children=[
            dcc.Graph(
                figure={
                    'data': [
                        {'x': df.index, 'y': df.iloc[:, 0], 'type': 'line', 'name': 'name'}],
                    'layout': {
                        'title': 'Dash Data Visualization'}
                }
            )
        ]
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


t = threading.Thread(target=server.run)
t.start()
wb.open_new('http://localhost:5000/')

if __name__ == '__main__':
    pass

