import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd
import os

import shutil



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app.external_stylesheets=external_stylesheets
	
layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '90%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '20px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename, date):
	content_type, content_string = contents.split(',')

	decoded = base64.b64decode(content_string)
	try:
		if 'csv' in filename:
            # Assume that the user uploaded a CSV file
			df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
		elif 'xls' in filename:
            # Assume that the user uploaded an excel file
			df = pd.read_excel(io.BytesIO(decoded))
		else:
			return html.Div([
				'Please upload csv or excel file.'
			])
	except Exception as e:
		print(e)
		return html.Div([
            'There was an error processing this file.'
        ])

	return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

filepath_projectbook = r'data\ProjectBook.csv'

@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
# def update_output(list_of_contents, list_of_names, list_of_dates):
    # if list_of_contents is not None:
        # children = [
            # parse_contents(c, n, d) for c, n, d in
            # zip(list_of_contents, list_of_names, list_of_dates)]
        # return children

def file_update(list_of_contents, list_of_names, list_of_dates):
	if list_of_contents is not None:
		for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
			if n == 'ProjectBook.csv': 
				#archive old projectbook
				#rename current projectbook with time stamp
				
				# dir_name = os.path.dirname(filepath)
				base_filename = os.path.splitext(filepath_projectbook)[0]
				filename_suffix = os.path.splitext(filepath_projectbook)[1]
				timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%I-%M-%S_%p")
				newfilepath = base_filename + timestamp + "." + filename_suffix
				shutil.copyfile(filepath_projectbook, newfilepath)
				#save the projectbook
				# c.save(filepath_projectbook)
				content_type, content_string = c.split(',')
				decoded = base64.b64decode(content_string)
				df_temp = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
				df_temp.to_csv(filepath_projectbook, index=False)
	
	return 'file saved.'
		