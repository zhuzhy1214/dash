import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output



# from layouts import layout1, layout2, home_page
# import callbacks
from apps import app, app1, uploadfile, home, app_projectbook

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):

	if pathname == '/apps/uploadfile':
		return uploadfile.layout
	elif pathname == '/apps/projectbook':
		# df, datatable_columns_dict, filter_columns = app_projectbook.load_df()
		return app_projectbook.dashboard_layout
	elif pathname == '/':
		return home.home_page
	else:
		return 'The page does not exist.'

if __name__ == '__main__':
    # app.run_server(debug=True )
	app.run_server(debug=True, port = 8051, host ='0.0.0.0')