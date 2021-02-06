import dash_core_components as dcc
import dash_html_components as html

home_page = html.Div([
	
	html.Br(),
    html.Div(html.H3('Project Book Home Page')),
    html.Br(),
    dcc.Link('Upload project book csv file', href='/apps/uploadfile'),
    html.Br(),
	html.Div(html.H3(' ')),
    dcc.Link('Go to project book dashboard', href='/apps/projectbook'),
])
