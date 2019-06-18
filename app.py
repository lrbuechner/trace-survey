# modules / packages
 
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import dash_daq as daq
import ast
import numpy as np
import json
from textwrap import dedent as d
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime as dt
import os
 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# this DateTime function will be taken care off ofline and factored 
# into the final db/csv used in the deployed version 
def DateTime(df):
    year = [] ; month = [] ; day = []
    for i in df['trd_exctn_dt']:
        i = str(i)
        year.append(i[:4])
        month.append(i[4:6])
        day.append(i[6:8]) 
    hour = [] ; minute = [] ; second = []
    for i in df['trd_exctn_tm']:
        i = i.split(':')
        hour.append(i[0])
        minute.append(i[1])
        second.append(i[2])
    dt = pd.DataFrame({'year':year,'month':month,'day':day,'hour':hour,'minute':minute,'second':second})
    df['datetime'] = list(pd.to_datetime(dt))

# data importing
df = pd.read_csv(os.path.join(os.path.dirname(__file__),'surv_data_test.csv'))
DateTime(df)
df['hold_index'] = df.index
ids = df['bond_sym_id'].unique()[:4]
 
# HTML/CSS 
app.layout = html.Div([

    html.H1([
        html.Img(src=app.get_asset_url('logo2.png')),
        ], style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto", 'padding-top': 20}
    ),

    html.Hr(style = {'background-color': '#6c1420', 'height': 10, 'border-color': '#6c1420', 'margin': 0, 'width': '1000%'}),
    html.H1(' ', style = {'height': 35}), # 50

    html.Div([ 
    dcc.Tabs(id = 'tabs', value = 'tab1', vertical = True, children = [
        
        # Tab 1 - Information Collection
        dcc.Tab(id = 'tab1', label = 'Info', value = 'tab1', disabled = False, children = [
             
            html.Div([
            html.H3('Personal Information', style = {'font-weight': 'bold', 'textAlign':'left', "display": "block","margin-left":"auto","margin-right":"auto"}),
            html.H6('Name'),
            dcc.Input(
                id = 'name',
                placeholder = 'Name: John Doe',
                type = 'text',
                value  = '',
                style = {'textAlign':'left'}
            ),
            html.H6('Email'),
            dcc.Input(
                id = 'email',
                placeholder = 'Email: johndoe@gmail.com',
                type = 'text',
                value  = ''
            ),
            html.H1(' '),
            html.H1(' '),
            html.H3('Experience', style = {'font-weight': 'bold'}),
            html.H6('Background'),
            dcc.RadioItems(
                id = 'professional-experience',
                options = [
                    {'label': 'Industry', 'value': 'indsutry'},
                    {'label': 'Academic', 'value': 'academic'},
                    {'label': 'Student', 'value': 'student'},
                    {'label': 'Other', 'value':'other'}
                ],
            ),
            html.H1(' '),
            html.H6('Have you worked with bond data before?'),
            dcc.RadioItems(
                id = 'bond-experience',
                options=[
                    {'label': 'Yes', 'value': 'yes'},
                    {'label': 'No', 'value': 'n'}
                ],
            ),
            html.H1(' '),
            html.Div([
                html.Button('Begin Survey', id='begin-survey', style = {'font-size': '100%'})
            ]),
        ], style = {'textAlign':'left', "display": "block", 'padding-right': 200, 'padding-left': 25, 'border-color': '#6c1420'})
        ]),
        
        # Tab 2 - The Actual Survey, might make this the 3rd tab and add an additional tab that includes a basic tutorial / motivation for this survey
        dcc.Tab(id = 'tab2', label = 'Survey', value ='tab2', disabled=True , children = [

            html.Div([
                dcc.Graph(
                    id='indicator-graphic',
                    style={
                        'height': 600,
                        'width': 1200,
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto"
                    },
                    config = {'scrollZoom': True}
                ),

                html.Div([dcc.RadioItems(
                    id = 'order-type',
                    options = [{'label': i, 'value': i} for i in ['Buy', 'Sell','Both']],
                    value = 'Both',
                    labelStyle = {'display': 'inline-block'},
                    style = {
                        'textAlign': 'center',
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto",})]
                ),
                
                html.Div([
                    html.Div([
                        html.Button('Confirm Selection', id='confirm-button', n_clicks = 0, style = {'font-size': '100%'})
                        ]),
                    ], style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"}
                ),
                
                html.Div(id='index-log', style = {'display':'none'}),
                html.Div(id='hidden', style = {'display':'none'}),
                html.Div(id = 'show-table')   
                ], style = { "display": "block", 'padding-right': 0} # or 100, OCD trigger lmao
            )   
        ]),
        
        # Final Tab - Summarize Information as well as provide information about me and prof / our university
        dcc.Tab(id = 'tab3', label = 'Summary', value ='tab3', disabled=True , children = [ 
            html.Div(id = 'codex-index', style = {'display':'none'}),
            html.Div(id = 'dump', style = {'display':'none'}),
            html.Div(id = 'formatted')
        ])
        ], colors={"primary": '#6c1420'})
    ], style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"}),

    # https://stackoverflow.com/questions/6127621/keeping-footer-at-the-bottom-of-window-on-site-that-scrolls-horizontal
    html.Footer(style = {'display':'block', 'background-color': '#6c1420', 'height': 50, 'margin': 0}) 
])
     
# callbacks for scatter plot interaction and data selection 
@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('order-type', 'value'),
    Input('confirm-button','n_clicks')])
def update_graph(order_type, conf_button):
    
    # control flow for end of survey
    if conf_button < len(ids):
 
        if conf_button == None:
            conf_button = 0
        
        # which timeseries/ cusip is currently being loaded
        click_tracker = conf_button 
        if click_tracker < 0:
            click_tracker = len(ids) + click_tracker
 
        bond_i = df[(df['bond_sym_id'] == ids[click_tracker])]
         
        # dealing with differnt types of bond order types for radio button customization
        if order_type == 'Both':
            price_type = ['B','S']
            colors = ['rgb(30, 201, 0)', 'rgb(229, 0, 0)']
            return {
                'data': [go.Scattergl(
                        x = bond_i[bond_i['rpt_side_cd'] == price_type[i]]['datetime'],
                        y = bond_i[bond_i['rpt_side_cd'] == price_type[i]]['rptd_pr'],
                        text = bond_i[bond_i['rpt_side_cd'] == price_type[i]]['entrd_vol_qt'],
                        name = ['Buy','Sell'][i],
                        mode = 'markers',
                        opacity = 0.7,
                        marker = {
                            'size': 5,
                            'color': colors[i],
                            'line': {'width': 0.5, 'color': 'white'}
                            },) for i in range(2)],
                'layout': go.Layout(
                        title='TRACE Outlier Classification | CUSIP: {}/{}'.format(click_tracker+1,len(ids)),
                        margin={'l': 50, 'b': 50, 't': 80, 'r': 80},
                        yaxis={'title':'Prices'},
                        legend={'x': 1, 'y': 1},
                        hovermode='closest',
                        clickmode = 'event+select'
                        )
            }
        else:
            if order_type == 'Buy':
                B_S = 'B'
                color = 'rgb(30, 201, 0)' # rgb(110, 226, 43)
            elif order_type == 'Sell':
                B_S = 'S'
                color = 'rgb(229, 0, 0)' # rgb(234, 35, 35)
                 
            bond_i = df[(df['bond_sym_id'] == ids[click_tracker]) & (df['rpt_side_cd'] == B_S)]
 
            return {
                'data': [go.Scattergl(
                        x = bond_i['datetime'],
                        y = bond_i['rptd_pr'],
                        text = bond_i['entrd_vol_qt'],
                        name = order_type,
                        mode = 'markers',
                        opacity = 0.7,
                        marker = {
                            'size': 5,
                            'color': color,
                            'line': {'width': 0.5, 'color': 'white'}
                            },
                        )],
                'layout': go.Layout(
                        title='TRACE Outlier Classification | CUSIP: {}/{}'.format(click_tracker+1,len(ids)),
                        margin={'l': 50, 'b': 50, 't': 80, 'r': 80},
                        xaxis={'title': 'Dates'},
                        yaxis={'title':'Prices'},
                        legend={'x': 1, 'y': 1},
                        hovermode='closest',
                        clickmode = 'event+select'
                        )
            }
 
# function that helps convert data from string into python objects. Storing data in HTML div
def make_list(x):
    if x == '[]':
        return []
    elif ',' not in x:
        X = x.strip('[]')
        return list(map(int,X.split()))
    else:
        return ast.literal_eval(x)
 
@app.callback(
    [Output('index-log','children'), 
    Output('codex-index','children'),
    Output('show-table','children')],
    [Input('indicator-graphic','selectedData'),
    Input('order-type', 'value'),
    Input('confirm-button','n_clicks'),
    Input('tabs','value')],
    [State('hidden','children'),
    State('index-log','children'),
    State('dump','children')]
)
def update_table(selected_data, order_type, conf_button, tab, hidden, current, prev_inds):
 
    if prev_inds == None:
        PREV = []
    else:
        PREV = ast.literal_eval(prev_inds)

    if conf_button < len(ids):
             
        if selected_data != None:

            if selected_data['points'] != []:
             
                # type manipulation for prev/next functionality
                if conf_button == None:
                    conf_button = 0
                click_tracker = conf_button 
                 
                # mapping pointNumber to index of global DataFrame
                buy = df[(df['bond_sym_id'] == ids[click_tracker]) & (df['rpt_side_cd'] == 'B')]
                sell = df[(df['bond_sym_id'] == ids[click_tracker]) & (df['rpt_side_cd'] == 'S')]
 
                fig_data = pd.DataFrame(selected_data["points"])[['curveNumber','pointNumber','y','text']]
 
                H = hidden.split('|')
                B = make_list(H[0])
                S = make_list(H[1])
 
                curve_buy = fig_data[(fig_data['curveNumber'] == 0) & ((fig_data['pointNumber']).isin(B) == False)]
                curve_sell = fig_data[(fig_data['curveNumber'] == 1) & ((fig_data['pointNumber']).isin(S) == False)]
                        
                if max(list(curve_buy['pointNumber'].values)+[-1]) < len(buy) and max(list(curve_sell['pointNumber'].values)+[-1]) < len(sell):
                    # collecting indicies 
                    b = list(buy.iloc[curve_buy['pointNumber'].values]['hold_index'].values)
                    s = list(sell.iloc[curve_sell['pointNumber'].values]['hold_index'].values)        
                    indicies = b+s
 
                    # manipulation for dataTable format
                    DT = df.loc[indicies]
                    DT['Datetime'] = DT['datetime']
                    DT['Price'] = DT['rptd_pr']
                    DT['Volume'] = DT['entrd_vol_qt']
                    DT['B/S'] = DT['rpt_side_cd']
                    DT = DT[['Datetime','Price','Volume','B/S']]

                    # returning dataTable
                    return ['{}|{}'.format(curve_buy['pointNumber'].values, curve_sell['pointNumber'].values), '{}'.format(indicies), \
                        html.Div([dash_table.DataTable( \
                            id = 'table', \
                            columns = [{"name": i, "id": i} for i in DT.columns], \
                            data = DT.to_dict("rows"), \
                            style_cell = {'textAlign': 'center','padding': '5px'}, \
                            style_as_list_view = True, \
                            style_cell_conditional=[{'if': {'column_id': 'Datetime'},'width': '100px'},{'if': {'column_id': 'Price'},'width': '100px'},{'if': {'column_id': 'Volume'},'width': '100px'}], \
                            style_header = {'backgroundColor': 'white', 'fontWeight': 'bold'}, \
                            n_fixed_rows=1, \
                            style_table={'maxHeight': '300px', 'maxWidth': '500px',"margin-left": "auto", "margin-right": "auto"})])]
                else:
                    return ['[]|[]','{}'.format(PREV),'']
            else:
                return ['[]|[]','{}'.format(PREV),'']
        else:
            return ['[]|[]','{}'.format(PREV),'']
    else:
        return ['[]|[]','{}'.format(PREV),'']
 
# upon tranition to next timeseries/bond - store data in page, keeps track of 
# indicies from official survey DB used to optimize filter 
@app.callback(
    [Output('indicator-graphic','selectedData'),
    Output('hidden','children'),
    Output('dump','children'),
    Output('formatted','children')],
    [Input('confirm-button','n_clicks')],
    [State('index-log','children'),
    State('hidden','children'),
    State('codex-index','children'),
    State('dump','children'),
    State('name','value'),
    State('email','value'),
    State('professional-experience','value'),
    State('bond-experience','value')]
)
def data_handler(clicks, child, hidden, codex, dump, name, email, pro_exp, bond_exp):

    if clicks == len(ids):
        my_dict = {
            'name': name, 'email': email, 
            'pro_exp': pro_exp, 
            'bond_exp': bond_exp, 
            'indicies': ast.literal_eval(dump)
        }
    else:
        my_dict = {}

    if codex == None and dump == None:
            Codex = []
    else:
        Codex = list(set(make_list(codex) + make_list(dump)))

    if child != None and hidden != None:
        # merging previously selected to current CUSIP
        C = child.split('|')
        B1 = make_list(C[0])
        S1 = make_list(C[1])
        H = hidden.split('|')
        B2 = make_list(H[0])
        S2 = make_list(H[1])
        B = B1 + B2
        S = S1 + S2 
        return [{"points": []},'{}|{}'.format(B,S),'{}'.format(Codex), '{}'.format(my_dict)]
    else:
        return [{"points": []},'[]|[]','{}'.format(Codex), '{}'.format(my_dict)]

# Tab transition/toggling 
@app.callback(
    [Output('tab1','disabled'),
    Output('tab2','disabled'),
    Output('tab3','disabled'),
    Output('tabs','value')],
    [Input('begin-survey','n_clicks'),
    Input('confirm-button','n_clicks')]
)
def next_tab1(begin_clicks, conf_clicks):
    if begin_clicks != 1:
        return [False,True,True,'tab1']
    elif begin_clicks == 1 and conf_clicks != len(ids):
        return [True, False, True,'tab2']
    elif conf_clicks == len(ids):
        return [True, True, False,'tab3']
 
if __name__ == '__main__':
    app.run_server(debug=True)
 
