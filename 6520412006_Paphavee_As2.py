import pandas as pd
import plotly.express as px
import dash
import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import requests

df = pd.read_csv('C:/Users/ACER/Downloads/5001/Starbucks.csv')

# Question 1
df1 = df[["Country", "Store Number"]][df.Country.isin(["TH", "MY", "VN"])].groupby("Country")["Store Number"].count().reset_index()
df1.rename(columns={"Store Number": "N_Store"}, inplace=True)


app = dash.Dash(__name__)


app.layout = html.Div([
    html.H1('The number of Starbucks stores in each province'),
    html.Div(
        children=[
            html.H2('Country Select'),
            dcc.Dropdown(
                id='country_dd',
                options=[
                    {'label': 'All Countries', 'value': 'ALL'},
                    {'label': 'Thailand', 'value': 'TH'},
                    {'label': 'Malaysia', 'value': 'MY'},
                    {'label': 'Vietnam', 'value': 'VN'},
                ],
                value='ALL',  
                style={'width': '200px', 'margin': '0 auto'}
            ),
            dcc.Graph(id='bar-chart')  
        ],
        style={'width': '350px', 'height': '450px', 'display': 'inline-block', 'vertical-align': 'top',
               'border': '1px solid black', 'padding': '20px'}
    ),
])


@app.callback(
    dash.dependencies.Output('bar-chart', 'figure'),
    dash.dependencies.Input('country_dd', 'value')
)
def update_bar_chart(selected_country):
    if selected_country == 'ALL':
        filtered_df1 = df1  
    else:
        filtered_df1 = df1[df1['Country'] == selected_country]
    fig = px.bar(filtered_df1, x='Country', y='N_Store', title=f'Count of Store by Country({selected_country})')
    return fig

if __name__ == '__main__':
    app.run_server(port=8050,debug=True) 
    
##------------------------------------------##


# Question 2
df2 = df[['Country', 'City', 'Store Number']][df['Country'].isin(['TH', 'MY', 'VN'])]
df2 = df2[['Country', 'City']].value_counts().reset_index().rename(columns={'count': 'Num_Store'}).sort_values(by='Num_Store', ascending=False)
df2

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Question 2"),

    dcc.Dropdown(
        id='country-dropdown',
        options=[
            {'label': 'All', 'value': 'All'},
            {'label': 'TH', 'value': 'TH'},
            {'label': 'VN', 'value': 'VN'},
            {'label': 'MY', 'value': 'MY'}
        ],
        value='All',
    ),

    dcc.Graph(id='treemap-chart'),

    dash_table.DataTable(id='table', columns=[{'name': col, 'id': col} for col in df2.columns])
])


@app.callback(
    Output('table', 'data'),
    Output('treemap-chart', 'figure'),
    Input('country-dropdown', 'value')
)
def update_components(input_country):
    filtered_df = df2[df2['Country'] == input_country] if input_country != 'All' else df2

    table_data = filtered_df.to_dict('records')

    fig2 = px.treemap(filtered_df,
                      path=['Country', 'City'],
                      values='Num_Store',
                      title=f'The Number of Starbucks Stores in {input_country}')

    return table_data, fig2


if __name__ == '__main__':
    app.run_server(port=8052, debug=True)

#------------------------------#

# Question 3

geojson_response = requests.get('https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json')
geojson_data = geojson_response.json()

df_map = df[df['Country'].isin(['TH'])]
df_map = df_map[df_map['City'].isin(['Bangkok', 'Phuket', 'Chiang Mai'])]
df_map.loc[df_map['City'] == 'Bangkok', 'City'] = 'Bangkok Metropolis'
df_store_counts = df_map.groupby('City')['Store Number'].nunique().reset_index().sort_values(by='Store Number', ascending=False)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='heat-map')
])

@app.callback(
    Output('heat-map', 'figure'),
    Input('heat-map', 'relayoutData')
)
def update_heat_map(relayoutData):
    fig3 = px.choropleth_mapbox(
        df_store_counts,
        geojson=geojson_data,
        locations='City',
        featureidkey="properties.name",
        color='Store Number',
        color_continuous_scale="matter_r",
        range_color=(0, df_store_counts['Store Number'].max()),
        mapbox_style="carto-positron",
        zoom=4,
        center={"lat": 13.7563, "lon": 100.5018}
    )

    fig3.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(title="Store Count")
    )

    return fig3

if __name__ == '__main__':
    app.run_server(port = 8053, debug=True)


