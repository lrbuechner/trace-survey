# modules / packages
 
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import dash_daq as daq
import dash_dangerously_set_inner_html

import ast
import numpy as np
import json
from textwrap import dedent as d
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime as dt
import os
import psycopg2

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
ids = df['bond_sym_id'].unique()
 
# HTML/CSS 
app.layout = html.Div([

    html.H1([
        #html.Img(src=app.get_asset_url('44.png'), style = {'height':'5%', 'width':'5%'}),
        html.Img(src=app.get_asset_url('logo2.png'), style = {'height':'25%', 'width':'25%'}),

        ], style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto",'padding-top': 20}
    ),

    html.Hr(style = {'background-color': '#6c1420', 'height': 10, 'border-color': '#6c1420', 'margin': 0, 'width': '100%'}), # '#307d9b'
    html.H1(' ', style = {'height': '2vh'}), # 50

    html.Div([ 
    dcc.Tabs(id = 'tabs', value = 'tab1', vertical = True, children = [
        
        # Tab 1 - Information Collection
        dcc.Tab(id = 'tab1', label = 'Info', value = 'tab1', disabled = False, children = [
             
            html.Div([
            html.H3('Personal Information', style = {'font-weight': 'bold', 'textAlign':'left', "display": "block","margin-left":"auto","margin-right":"auto"}),
            html.H6('Name'),
            dcc.Input(
                id = 'name',
                placeholder = 'John Doe',
                type = 'text',
                value  = '',
                style = {'textAlign':'left'}
            ),
            html.H6('Organization'),
            dcc.Input(
                id = 'organization',
                placeholder = 'College University',
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
            html.H6('For how many years have you worked with bond data?'),

            dcc.Slider(
                id = 'bond-experience',
                marks={0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'10+'},
                min=0,
                max=10,
                value=0,
                className = 'rc-slider'
            ),

            html.H1(' ', style = {'padding-bottom':30}),
            html.Div([
                dcc.ConfirmDialogProvider(
                            children=html.Button(
                                'Begin Survey',
                                style = {'font-size': '100%'},
                            ),
                            id='begin-survey',
                            message='Please double check your info!'
                        ),
            ]),
            html.Div(id='userinfo-hidden', style = {'display':'none'})

        ], style = {'textAlign':'left', "display": "block", 'padding-right': 200, 'padding-left': 25, 'border-color': '#6c1420'})
        ]),
        
        # SURVEY TAB
        dcc.Tab(id = 'tutorial-tab', label = 'Tutorial', value = 'tutorial-tab', disabled = True, children = [
            
            html.Div([
                #html.Div([html.Iframe(src="https://www.youtube.com/embed/iWZdz9_Ls_w", width =  1189/2, height = 669/2)]),
                dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
                    <iframe width="1280" height="720" src="https://www.youtube.com/embed/f7Zik6F6uCs" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                '''),
                html.Button('Complete Tutorial', id = 'survey-button', style = {'font-size': '100%'}, n_clicks = 0)
            ],  style={'textAlign':'center',"display": "block","margin-left":'5vw',"margin-right":'5vw', 'padding-right': 120})
        ]),

        # Tab 2 - The Actual Survey, might make this the 3rd tab and add an additional tab that includes a basic tutorial / motivation for this survey
        dcc.Tab(id = 'tab2', label = 'Survey', value ='tab2', disabled=True , children = [

            html.Div([
                dcc.Graph(
                    id='indicator-graphic',
                    style={
                        'height': '45vh',
                        'width': '90vh',
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
                        "margin-right": "auto",
                        'padding-bottom':5})]
                ),
                
                html.Div([
                    html.Div([
                        html.Button('Confirm Selection', id='confirm-button', n_clicks = 0, style = {'font-size': '100%'})
                        ], style = {'padding-bottom':10}),
                        dcc.ConfirmDialogProvider(
                            children=html.Button(
                                'Finish',
                                style = {'font-size': '100%'},
                            ),
                            id='exit-danger',
                            message='Are you sure you want to finish the survey early?'
                        ),
                    ], style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"}
                ),
                html.H3(' '),
                html.Div('Note: You can finish the survey at any point in time!', style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"}),
                html.H3(' '),

                html.Div(id='index-log', style = {'display':'none'}),
                html.Div(id='hidden', style = {'display':'none'}),
                html.Div(id = 'show-table')   
                ], style = { "display": "block", 'padding-right': 120} # or 100, OCD trigger lmao
            )   
        ]),
        
        # Final Tab - Summarize Information as well as provide information about me and prof / our university
        dcc.Tab(id = 'tab3', label = 'Summary', value ='tab3', disabled=True , children = [ 
            html.Div(id = 'codex-index', style = {'display':'none'}),
            html.Div(id = 'dump', style = {'display':'none'}),
            html.Div(id = 'formatted', style = {'display':'none'}),

            # reciept
            html.H1(' ', style = {'padding-top':150}),
            html.Div([
                html.H1('Thank You!',style = {'font-size': '300%','textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"})
                ], style = {'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto", 'padding-right': 420, 'padding-left': 300}
            ),
            
        

        ])
        ], colors={"primary": '#6c1420'}),

        html.H1(' ', style = {'height': 50}), 

    ], style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"}),

    # https://stackoverflow.com/questions/6127621/keeping-footer-at-the-bottom-of-window-on-site-that-scrolls-horizontal
    html.Footer(style = {'display':'block', 'background-color': '#6c1420', 'height': '3vh', 'margin-top': '10vh'}) 

    ], style = {'height': '100vh', 'width': '100vw'}
)
     
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
                        opacity = 1,
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

def default(o):
    if isinstance(o, np.int64): return int(o)  
    raise TypeError
 
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
        prev_inds = json.loads(prev_inds)
        PREV = prev_inds['inds']

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

                hidden = json.loads(hidden)
                B = hidden['buy']
                S = hidden['sell']
 
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
                    return [json.dumps({'buy': curve_buy['pointNumber'].values.tolist(), 'sell': curve_sell['pointNumber'].values.tolist()}, default=default), json.dumps({'inds':indicies}, default=default), \
                        html.Div([dash_table.DataTable( \
                            id = 'table', \
                            columns = [{"name": i, "id": i} for i in DT.columns], \
                            data = DT.to_dict("rows"), \
                            style_cell = {'textAlign': 'center','padding': '5px'}, \
                            style_as_list_view = True, \
                            style_cell_conditional=[{'if': {'column_id': 'Datetime'},'width': '100px'},{'if': {'column_id': 'Price'},'width': '100px'},{'if': {'column_id': 'Volume'},'width': '100px'}], \
                            style_header = {'backgroundColor': 'white', 'fontWeight': 'bold'}, \
                            n_fixed_rows = 1, \
                            style_table={'height': '20vh', 'width': '50vw', 'maxHeight': '300px', 'maxWidth': '500px',"margin-left": "auto", "margin-right": "auto"})])
                        ]
                else:
                    return [json.dumps({'buy': [], 'sell': []}), json.dumps({'inds': PREV}, default=default),'']
            else:
                return [json.dumps({'buy': [], 'sell': []}), json.dumps({'inds': PREV}, default=default),'']
        else:
            return [json.dumps({'buy': [], 'sell': []}), json.dumps({'inds': PREV}, default=default),'']
    else:
        return [json.dumps({'buy': [], 'sell': []}), json.dumps({'inds': PREV}, default=default),'']
 
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
    State('organization','value'),
    State('professional-experience','value'),
    State('bond-experience','value')]
)
def data_handler(clicks, child, hidden, codex, dump, name, organization, pro_exp, bond_exp):

    if clicks >= 1:

        new_inds = json.loads(codex)['inds']      

        connection = psycopg2.connect(
            user="ojbgjqmyqdpzkf",
            password="d4001165d169a3add23e7c8d2ba4fed7db708838fca1a94977eb6977de68f894",
            host="ec2-54-83-33-14.compute-1.amazonaws.com",
            port="5432",
            database="d1khr7vbop54p0"
        )
        cursor = connection.cursor()
        update_statement = """ 
            UPDATE survey_results 
            SET indicies = array_cat(indicies, %s) 
            WHERE username = %s and organization = %s """
            
        record_to_update = (str(new_inds).replace('[','{').replace(']','}'), name, organization)
        cursor.execute(update_statement, record_to_update)
        connection.commit()
        cursor.close()
        connection.close()

    if codex == None and dump == None:
        Codex = []
    else:
        codex = json.loads(codex)
        dump = json.loads(dump)
        Codex = list(set(codex['inds'] + dump['inds']))

    if child != None and hidden != None:
        # merging previously selected to current CUSIP
        child = json.loads(child)
        B1 = child['buy']
        S1 = child['sell']
        hidden = json.loads(hidden)
        B2 = hidden['buy']
        S2 = hidden['sell']
        B = B1 + B2
        S = S1 + S2 
        return [{"points": []}, json.dumps({'buy': B, 'sell': S}), json.dumps({'inds': Codex}, default=default), '{}']
    else:
        return [{"points": []}, json.dumps({'buy': [], 'sell': []}), json.dumps({'inds': Codex}, default=default), '{}']

# user information 
@app.callback(
    Output('userinfo-hidden','children'),
    [Input('begin-survey','submit_n_clicks')],
    [State('name','value'),
    State('organization','value'),
    State('professional-experience','value'),
    State('bond-experience','value')]
)
def create_user(clicks, name, organization, pro_exp, bond_exp):

    if clicks == 1:
        user_information = {
            'username': name,
            'organization': organization,
        }
        connection = psycopg2.connect(
            user="ojbgjqmyqdpzkf",
            password="d4001165d169a3add23e7c8d2ba4fed7db708838fca1a94977eb6977de68f894",
            host="ec2-54-83-33-14.compute-1.amazonaws.com",
            port="5432",
            database="d1khr7vbop54p0"
        )
        cursor = connection.cursor()
        indicies = []
        insert_statement = """ INSERT INTO survey_results (username, organization, pro_exp, bond_exp, indicies) VALUES (%s,%s,%s,%s,%s)"""
        record_to_insert = (name, organization, pro_exp, bond_exp, indicies)
        cursor.execute(insert_statement, record_to_insert)
        connection.commit()
        cursor.close()
        connection.close()
        return user_information
    else:
        return ''

# Tab transition/toggling 
@app.callback(
    [Output('tab1','disabled'),
    Output('tutorial-tab','disabled'),
    Output('tab2','disabled'),
    Output('tab3','disabled'),
    Output('tabs','value')],
    [Input('begin-survey','submit_n_clicks'),
    Input('confirm-button','n_clicks'),
    Input('survey-button','n_clicks'),
    Input('exit-danger','submit_n_clicks')]
)
def next_tab1(begin_clicks, conf_clicks, surv_clicks, finish):

    # finish survey early
    if finish == 1:
        conf_clicks = len(ids)

    # tab management
    if begin_clicks != 1:
        return [False,True,True,True,'tab1']
    elif begin_clicks == 1 and surv_clicks == 0 and conf_clicks != len(ids):
        return [True, False, True, True,'tutorial-tab']
    elif begin_clicks == 1 and surv_clicks == 1 and conf_clicks != len(ids):
        return [True, True, False, True,'tab2']
    elif conf_clicks == len(ids):
        return [True, True,True, False,'tab3']
 
if __name__ == '__main__':
    app.run_server(debug=True)
 
