import os
import pathlib

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State, ALL
import dash_table

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go
import plotly.express as px

from app import app

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# external_stylesheets=[dbc.themes.BOOTSTRAP]

#check file last modified time

# def load_df():
df = pd.read_csv('data\ProjectBook.csv')
df['Project Cost ($K)'] = df.apply(lambda x: 'TBD' if x['Planning or Post-Planning? '] == 'Planning' else x['Project Cost ($K)'], axis=1)

table_columns = ['SHOPP ID', 'Caltrans District', 'County', 'Route', 'Begin Mile', 'End Mile',
	   'Primary Work', 'Planning or Post-Planning? ', 'Advertised Year',
	   'Project Cost ($K)', 'SB-1 Priority']
table_column_datatypes = ['numeric','numeric','text','text', 'text','text',
		'text','text','text',
		'numeric','text']
		
datatable_columns_dict = [{"name": i, "id": i, "type": j} for i, j in zip(table_columns, table_column_datatypes)]

filter_columns = ['Caltrans District','CA State Assembly District', 'CA State Senate District',
	   'U.S. Congressional District', 'MPO/RTPA', 'County', 'Route', 'Project Status','Advertised Year','Primary Work']
	# print('updating the df')
	# return df, 	datatable_columns_dict, filter_columns
	
# df, datatable_columns_dict, filter_columns = load_df()

#generate dropdown for pattern matching callback
dropdown_containers = []
for i, column in enumerate(filter_columns): 
	new_dropdown = dcc.Dropdown(
		id={
			'type': 'filter-dropdown',
			'index': i
		},
		options=[{'label': str(n), 'value': str(n)} for n in sorted(df[column].unique())],
		placeholder = '(All)',
		multi = True,
	)
	dropdown_container=	html.Div([
									html.P(children=column),
									html.Div([new_dropdown])
								],style={'width': '20%', 'display': 'inline-block'}
						)
	dropdown_containers.append(dropdown_container)

#read project activity data
df_a = pd.read_csv('data\ProjectActivities.csv')
df_a['Supplementary Activity'] = df_a['Supplementary Activity'].str.strip()
df_a['Supplementary Activity'] = df_a['Supplementary Activity'].str.replace('Do Not Include','')
unique_activity = sorted(list(df_a['Supplementary Activity'].unique()))
unique_activity = [i for i in unique_activity if i] 
df_a = df_a.drop_duplicates(['SHOPP ID', 'Supplementary Activity'])

df_a['Supplementary Activity List'] = df_a['Supplementary Activity'] 

def join_activities(activities):
	temp = []
	for a in activities:
		if a != '':
			temp.append(a)
	return '; '.join(temp)
	
df_s = df_a.groupby('SHOPP ID')['Supplementary Activity'].apply(join_activities).reset_index()
df_l = df_a.groupby('SHOPP ID')['Supplementary Activity List'].apply(list).reset_index()
df_ls = df_s.merge(df_l, left_on="SHOPP ID", right_on="SHOPP ID")

df = df.merge(df_ls, left_on="SHOPP ID", right_on="SHOPP ID")

#generate dropdown for project activity list
new_dropdown_1 = dcc.Dropdown(
		id='project_activity',
		options=[{'label': str(n), 'value': str(n)} for n in unique_activity],
		placeholder = '(All)',
		multi = True,
	)
	
dropdown_container_1= html.Div([
							html.P(children='Project Activity'),
							html.Div(new_dropdown_1)
							],style={'width': '100%', 'display': 'inline-block'}
						)
#generate inputbox for project activity search 
input_projectactivitysearch_html = html.Div([
									html.P(children='Search within Project Activity'),
									html.Div([dcc.Input(
													id="project_activity_search",
													placeholder="type in keywords...",
													debounce = True
												)],style={'width': '100%', 'display': 'inline-block'})
										])

# scatter_mapbox figure
fig_template = go.layout.Template()
fig_template.data.scattermapbox = [go.Scattermapbox(
				selected=go.scattermapbox.Selected(
					marker = {
						"color":"red",
						"size":10
						}
					),
				# autosize=True,
				# unselected=go.scattermapbox.Unselected(
									# marker = {
										# "color":"blue",
										# "size":15
										# }
									# ),
)]

fig = px.scatter_mapbox(df, lat="Latitude to use", lon="Longitude to use", hover_name="SHOPP ID", hover_data=['Project Location'], zoom=5, template = fig_template) # color_discrete_sequence=["fuchsia"],
fig.update_layout(mapbox_style="open-street-map", height = 800)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})	


dcc_scattergeo=	dcc.Graph(
		id="scatter_geo",
		figure=fig,
	)
	
scatter_geo_container = html.Div( children=[dcc_scattergeo, ], )

#Project Details Block
project_details_html = html.Div(id='project_details',)
	
#datatable
html_table= html.Div(id = 'html_data_table',
    children = [
		dash_table.DataTable(
			id='data_table',
			columns=datatable_columns_dict,
			data=df.to_dict("rows"),
			filter_action="native",
			sort_action="native",
			sort_mode="multi",
			column_selectable="single",
			# row_selectable="single",
			# row_deletable=True,
			# selected_columns=[],
			# selected_rows=[],
			page_action="native",
			page_current= 0,
			page_size= 20,
			# style_as_list_view=True,
			style_cell={'padding': '5px'},
			style_header={
				'backgroundColor': 'white',
				'fontWeight': 'bold'}
		)
	]
)	
dashboard_layout = [html.Br(),
        dbc.Row([
			dbc.Col(html.Img(id="logo", src=app.get_asset_url("Caltran_Logo.png")),
							width={'size': 1, 'offset': 0},
							),
			dbc.Col(html.H1(children="SHOPP Ten-Year Project Book (July 2020)"),
							width={'size': 6, 'offset':0},
							),
			dbc.Col(html.H3(children="Number of Projects:"),
							width={'size': 3, 'offset':2},
							),
		]),
        dbc.Row([dbc.Col( html.P(
                    id="description",
                    children=["Accessibility Assistance: Caltrans makes every attempt to ensure our online content is accessible. Due to variances between assistive technologies, there may be portions of this content which is not accessible. We are committed to providing alternative access to the content.  Please see the SHOPP Ten Year Book PDF document on the Caltrans Asset Management website ", html.A(children = 'https://dot.ca.gov/programs/asset-management', href = 'https://dot.ca.gov/programs/asset-management',target='_blank'),". Should you need additional assistance, please contact us at (916) 654-2852 or visit ",html.A(children = 'https://dot.ca.gov/request-ada-compliant-documents.', href = 'https://dot.ca.gov/request-ada-compliant-documents'),],
					),
					width={'size': 8, 'offset':1},
				),
				dbc.Col(html.H4(id = 'project_counts', children = [],), 
					width={'size': 1, 'offset':0}),
        ]),
		dbc.Row(dbc.Col(html.Br())),
		
		dbc.Row([dbc.Col(html.Div(children=dropdown_containers), width={'size': 12, "offset": 0,})]), 
		dbc.Row(dbc.Col(html.Br())),
		dbc.Row([dbc.Col(dropdown_container_1,width={'size': 4, 'offset':0}), dbc.Col(input_projectactivitysearch_html, width={'size': 3, 'offset':0})]),
		dbc.Row(dbc.Col(html.Br())),
		dbc.Row([dbc.Col(html.H3("SHOPP Projects Map", style = {'font-weight': 'bold'}),width={'size': 5, "offset": 0}), 
				dbc.Col(html.H3('Details of Selected Project:', style = {'font-weight': 'bold'}),width={'size': 7, "offset": 0})]),
		dbc.Row(dbc.Col(html.P("Click a project in the map/table to view project details."),)),
        dbc.Row(
            [
                dbc.Col(scatter_geo_container, width={'size': 5, "offset": 0}
                        ),
                dbc.Col(project_details_html,  width={'size': 7, "offset": 0}
                        ),
            ]),
		dbc.Row(dbc.Col(html.Br())),
		dbc.Row([dbc.Col(html.H3("SHOPP Projects Table", style = {'font-weight': 'bold'}),width={'size': 6, "offset": 0}), 
				]),
		dbc.Row(dbc.Col(html.P("Click a project in the map/table to view project details."),)),					
		dbc.Row(dbc.Col(html_table))
	]


#update filter options
@app.callback([Output({'type': 'filter-dropdown', 'index': ALL}, 'options'),
				Output('project_activity', 'options')],
			[Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
			Input('project_activity', 'value'),
			Input('project_activity_search', 'value')]
)

def update_filter_options(filter_selected_values, projectactivity_filter_values, projectactivity_search_value):

	df2 = df
	if projectactivity_filter_values and len(projectactivity_filter_values) > 0:
		df2 = df2[df2['Supplementary Activity List'].apply(lambda x: any([a in x for a in projectactivity_filter_values]))]
	
	if projectactivity_search_value and len(projectactivity_search_value) > 0:
		df2=df2[df2['Supplementary Activity'].str.contains(projectactivity_search_value, na=False, case=False)]
		
	all_options = []
	for (i, _) in enumerate(filter_selected_values):
		dff = df2
		# print(dff.shape)
		for (j, values) in enumerate(filter_selected_values):
			if values and len(values) > 0 and (i != j): 
				dff = dff[dff[filter_columns[j]].isin(values)]
		new_options = [{'label': str(n), 'value':str(n)} for n in sorted(dff[filter_columns[i]].unique())]
		
		all_options.append(new_options)
		
	#append the project activity filter

	df2 = df
	if projectactivity_search_value and len(projectactivity_search_value) > 0:
		df2=df[df['Supplementary Activity'].str.contains(projectactivity_search_value, na=False, case=False)]
		
	dff = df2
	for (j, values) in enumerate(filter_selected_values):
		if values and len(values) > 0 : 
			dff = dff[dff[filter_columns[j]].isin(values)]
			
	filtered_unique_activity =[] 
  
	# Iterate over each row 
	for index, rows in dff.iterrows(): 
		# Create list for the current row 
		my_list =rows['Supplementary Activity List']
		  
		# append the list to the final list 
		filtered_unique_activity.extend(my_list) 
	filtered_unique_activity =list(set(filtered_unique_activity))
	filtered_unique_activity = [i for i in filtered_unique_activity if i] 
	projectactivity_options = [{'label': str(n), 'value':str(n)} for n in sorted(filtered_unique_activity)]
	return [all_options, projectactivity_options]

#update project counts
@app.callback(Output('project_counts', 'children'),
			[Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
			Input('project_activity', 'value'),
			Input('project_activity_search', 'value')]
)
def update_project_counts(filter_selected_values,projectactivity_filter_values, projectactivity_search_value):
	#find out which is the trigger, 
	#get the values from other inputs
	
	if projectactivity_filter_values and len(projectactivity_filter_values) > 0:
		df2 = df[df['Supplementary Activity List'].apply(lambda x: any([a in x for a in projectactivity_filter_values]))]
	else: 
		df2 = df
		
	if projectactivity_search_value and len(projectactivity_search_value) > 0:
		df2=df2[df2['Supplementary Activity'].str.contains(projectactivity_search_value, na=False, case=False)]

	dff = df2
	
	for (i, values) in enumerate(filter_selected_values):
		if values and len(values) != 0: 
			dff = dff[dff[filter_columns[i]].isin(values)]
	
	return [dff.shape[0]]
	
#update graph
@app.callback(Output('scatter_geo', 'figure'),
			[Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
			Input('project_activity', 'value'),
			Input('project_activity_search', 'value')]
)
def update_gragh(filter_selected_values,projectactivity_filter_values, projectactivity_search_value):
	#find out which is the trigger, 
	#get the values from other inputs
	
	
	# df, datatable_columns_dict, filter_columns = load_df()
	
	if projectactivity_filter_values and len(projectactivity_filter_values) > 0:
		df2 = df[df['Supplementary Activity List'].apply(lambda x: any([a in x for a in projectactivity_filter_values]))]
	else: 
		df2 = df
		
	if projectactivity_search_value and len(projectactivity_search_value) > 0:
		df2=df2[df2['Supplementary Activity'].str.contains(projectactivity_search_value, na=False, case=False)]

	dff = df2
	
	for (i, values) in enumerate(filter_selected_values):
		if values and len(values) != 0: 
			dff = dff[dff[filter_columns[i]].isin(values)]


	fig = px.scatter_mapbox(dff, lat="Latitude to use", lon="Longitude to use", hover_name="SHOPP ID", hover_data=['Project Location'], zoom=5, template = fig_template) 
	fig.update_layout(mapbox_style="open-street-map")
	fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
	
	return fig

#update data table
@app.callback(Output('html_data_table', 'children'),
			[Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
			Input('project_activity', 'value'),
			Input('project_activity_search', 'value'),
			Input('scatter_geo', 'selectedData' ),
			]
)
def update_table(filter_selected_values, projectactivity_filter_values, projectactivity_search_value, graph_selected_data):
	#find out which is the trigger, 
	#get the values from other inputs
	
	# df, datatable_columns_dict, filter_columns = load_df()
	
	ctx = dash.callback_context
	if not ctx.triggered:
		raise PreventUpdate
	else:
		changed_object = ctx.triggered[0]['prop_id'].split('.')[0]
		
	if changed_object == 'scatter_geo' and graph_selected_data: 
		dff = df
		pt_data = graph_selected_data["points"]
		values = [pt_dict.get('hovertext') for pt_dict in pt_data]
		dff = dff[dff['SHOPP ID'].isin(values)]
	else:	
		if projectactivity_filter_values and len(projectactivity_filter_values) > 0:
			df2 = df[df['Supplementary Activity List'].apply(lambda x: any([a in x for a in projectactivity_filter_values]))]
		else: 
			df2 = df
			
		if projectactivity_search_value and len(projectactivity_search_value) > 0:
			df2=df2[df2['Supplementary Activity'].str.contains(projectactivity_search_value, na=False, case=False)]

		dff = df2
		
		for (i, values) in enumerate(filter_selected_values):
			if values and len(values) != 0: 
				dff = dff[dff[filter_columns[i]].isin(values)]
	
	
	# data = dff[table_columns].to_dict("rows")
	datatable =	dash_table.DataTable(
			id='data_table',
			columns=datatable_columns_dict,
			data=dff.to_dict("rows"),
			filter_action="native",
			sort_action="native",
			sort_mode="multi",
			column_selectable="single",
			# row_selectable="single",
			# row_deletable=True,
			# selected_columns=[],
			# selected_rows=[],
			page_action="native",
			page_current= 0,
			page_size= 20,
			# style_as_list_view=True,
			style_cell={'padding': '5px'},
			style_header={
				'backgroundColor': 'white',
				'fontWeight': 'bold'}
			)
	
	return [datatable]

fig1_template = go.layout.Template()
fig1_template.data.scattermapbox = [go.Scattermapbox(
				# unselected=go.scattermapbox.Unselected(
									# marker = {
										# "color":"red",
										# "size":20
										# }
									# ),
				marker=go.scattermapbox.Marker(
					size=20,
					# color=['rgb(242, 177, 172)'],
					opacity=0.7,
					# symbol = ['home']
				),
				hoverinfo = 'skip',
				mode = 'markers+text',

)]

def generate_project_detail_html(SHOPP_id):
	temp = df[df['SHOPP ID'] == SHOPP_id]
	# print(temp['Project Location'].values[0])
	# print(temp)
		#update fig1
	fig1 = px.scatter_mapbox(temp, lat="Latitude to use", lon="Longitude to use", text='Project Location', zoom=10, template = fig1_template) 
	
	fig1.update_layout(mapbox_style="open-street-map", height = 300, width = 500)
	fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})	

	dcc_scattergeo1=dcc.Graph(
			id="scatter_geo_small",
			figure = fig1,
			config={
				'displayModeBar': False
			}
		)
		
	project_detail_html = html.Div(children = [
		html.Table( children = [
			html.Tr(children = [
				html.Th('SHOPP ID:', style={'min-width':'150px'}),
				html.Td(SHOPP_id),
				html.Th('Project Location:'),
				html.Td(temp['Project Location'].values[0]),
			]),
			html.Tr(children = [
				html.Th('Project Description:'),
				html.Td(temp['Project Description'].values[0], colSpan="3"),],),
			html.Tr(children = [
				html.Th('Project Status:'),
				html.Td(temp['Project Status'].values[0]),
				html.Th('Advertised Year:'),
				html.Td(temp['Advertised Year'].values[0]),]
			),

			html.Tr(children = [
				html.Th('Primary Work:'),
				html.Td(temp['Primary Work'].values[0]),
				html.Th('Primary Scope:'),
				html.Td(temp['Primary Scope'].values[0])
			]),
			
			html.Tr(children = [
				html.Th('Contact:'),
				html.Td(temp['Organization'].values[0], colSpan="3"),]),
			html.Tr(children = [
				html.Th('Stress Address:'),
				html.Td(temp['Street Address'].values[0]),
				html.Th('Mailing Address:'),
				html.Td(temp['Mailing Address'].values[0])]),

			html.Tr(children = [
				html.Th('Phone:'),
				html.Td(temp['Phone'].values[0]),
				html.Th('Email:'),
				html.Td(temp['Email'].values[0])]),
				
			html.Tr(children = [
				html.Th('District Project Portal:'),
				html.Td(html.A(children = 'District Project Portal', href = temp['District Portal Link'].values[0],target='_blank')),
				html.Th('Linkes To External Site:'),
				html.Td('') if pd.isnull(temp['Project Link'].values[0]) else html.Td(html.A(children = 'Link', href = temp['Project Link'].values[0],target='_blank')),

				]),
				
			html.Tr(children = [
				html.Th('Project Activities:'),
				html.Td(temp['Supplementary Activity'].values[0], colSpan="3"),]),
			
			#add zoomed in map
			html.Tr(children = [html.Th(['Project Zoom In Map or ', html.A(children = 'Google Map', href = 'https://www.google.com/maps/?q={},{}'.format(temp['Latitude to use'].values[0], temp['Longitude to use'].values[0]),target='_blank')]), html.Td(dcc_scattergeo1, colSpan="3"),]),
			]),
	], 
	# style={'width': '100%', 'display': 'inline-block',  'border-spacing': '0px'}
	)
	return project_detail_html
	
#update project details 
@app.callback([Output('project_details', 'children')],
			[Input("scatter_geo", "clickData"), 
			Input("data_table", "derived_viewport_data"),
			Input("data_table", "selected_cells")]
)
def update_project_details(graph_clickData, derived_viewport_data, selected_cells):
	ctx = dash.callback_context
	init_SHOPP_ID = 20275
	if not ctx.triggered:
		# return [html.H4('Click a project in the map/table to view project details.')]
		html_text = generate_project_detail_html(init_SHOPP_ID)
		changed_object ='none'
	else:
		changed_object = ctx.triggered[0]['prop_id'].split('.')[0]
			
	if changed_object == 'scatter_geo': 
		if graph_clickData is None:
			# return [html.H4('Click a project in the map/table to view project details.')]
			html_text = generate_project_detail_html(init_SHOPP_ID)
		else:
			pt_data = graph_clickData["points"][0]
			html_text = generate_project_detail_html(pt_data.get('hovertext'))
			return [html_text]

	elif changed_object == 'data_table':
		if selected_cells is None or len(selected_cells) == 0 : 
			# return [html.H4('Click a project in the map/table to view project details.')]
			html_text= generate_project_detail_html(init_SHOPP_ID)
		else:
			selected_row=derived_viewport_data[selected_cells[0].get('row')] 
			html_text = generate_project_detail_html(selected_row.get('SHOPP ID'))
	return [html_text]
			

# if __name__ == "__main__":
    # app.run_server(debug=True, port = 8051)
    # # app.run_server(debug=True, port = 8051, host ='0.0.0.0')
