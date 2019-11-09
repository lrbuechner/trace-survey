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
import psycopg2

# dash plotly 
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# database connection 
connection = psycopg2.connect(
            user="user",
            password="password",
            host="granny",
            port="able",
            database="data"
)
cursor = connection.cursor()

# querying unique cusips
query = """SELECT DISTINCT cusip_id FROM trace_lean"""
unique_cusips = pd.read_sql_query(query, connection)['cusip_id'].values
# shuffling cusips
np.random.shuffle(unique_cusips)
 
# HTML/CSS 
app.layout = html.Div([

    html.H1([
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
        
        # Tab 2 - The Actual Survey, might make this the 3rd tab and add an additional tab that includes a basic tutorial / motivation for this survey
        dcc.Tab(id = 'tab2', label = 'Survey', value ='tab2', disabled=True , children = [

            html.Div([
                dcc.Graph(
                    id='indicator-graphic',
                    style={
                        'height': '45vh',
                        'width': '55vw',
                        'max-height': 720,
                        'min-height': 480,
                        'max-width': 1280,
                        'min-width': 720,
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto",
                        
                    },
                    config = {'scrollZoom': True, 'showTips': True, 'displaylogo': False, 'doubleClick': 'reset', 
                    'modeBarButtonsToRemove': ['toImage', 'zoomIn2d', 'zoomOut2d', 'select2d', 'autoScale2d',
                    'autoScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian']}
                ),

                html.Div([dcc.Checklist(
                    id = 'order-type',
                    options=[
                        {'label': 'Buy', 'value': 'B'},
                        {'label': 'Sell', 'value': 'S'},
                        {'label': 'Inter-Dealer', 'value': 'D'}
                    ],
                    value=['B', 'S', 'D'],
                    labelStyle={'display': 'inline-block'},
                    style = {
                        'textAlign': 'center',
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto",
                        'padding-bottom':5})
                ]),
                
                html.Div([
                    html.Div([
                        html.Button('Confirm Selection', id='confirm-button', n_clicks = 0, style = {'font-size': '100%'})
                        ], style = {'padding-bottom':10}),
                        dcc.ConfirmDialogProvider(
                            children=html.Button(
                                'Finish',
                                style = {'font-size': '100%'},
                            ),
                            id='finish-surv',
                            message='Are you sure you want to finish the survey early?'
                        ),
                    ], style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"}
                ),
                html.H3(' '),
                html.Div('Note: You can finish the survey at any point in time!', style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"}),
                html.H3(' '),

                html.Div(id = 'data-table'),
                html.Div(id='index-log', style = {'display':'none'}),
                html.Div(id='hidden', style = {'display':'none'})
                   
                ], style = { "display": "block", 'padding-right': 120} # or 100, OCD trigger lmao
            )   
        ]),
        
        # Final Tab - Summarize Information as well as provide information about me and prof / our university
        dcc.Tab(id = 'tab3', label = 'Summary', value ='tab3', disabled=True , children = [ 

            # hidden divs
            html.Div(id = 'codex-index', style = {'display':'none'}),
            html.Div(id = 'dump', style = {'display':'none'}),
            html.Div(id = 'formatted', style = {'display':'none'}),
            html.Div(id = 'feedback-hidden', style = {'display':'none'}),
            # feedback / reciept
            html.Div([
                html.H1('Thank You!',style = {'font-size': '300%','textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"})
                ], style = {'textAlign':'center',"display": "block",
                "margin-left":"auto","margin-right":"auto", 'padding-right': 420, 'padding-left': 300, 'padding-top':150}
            ),
            html.Div([
                html.H6('Feedback', style = {'padding-right': 420, 'padding-left': 300,'padding-top': 25}),
                html.Div([
                    html.Div([
                        dcc.Textarea(
                            id = 'feedback',
                            placeholder="Optional: Your thoughts on the survey",
                            value='',
                            style={'width': '30vw', 'height': '5vh',
                                'textAlign':'left',"display": "block",
                                "margin-left":"auto","margin-right":"auto"}
                        ),
                        html.Div([
                        html.Button('Submit', id = 'end', style = {'font-size': '100%'})
                        ], style = {'padding-top':10})

                    ], style = {'padding-right': 420, 'padding-left': 300})    
                ])  
            ])      
        ])

        ], colors={"primary": '#6c1420'}),

        html.H1(' ', style = {'height': 50}), 

    ], style={'textAlign':'center',"display": "block","margin-left":"auto","margin-right":"auto"}),

    # https://stackoverflow.com/questions/6127621/keeping-footer-at-the-bottom-of-window-on-site-that-scrolls-horizontal
    html.Footer(style = {'display':'block', 'background-color': '#6c1420', 'height': '3vh', 'margin-top': '10vh'}) 

    ], style = {'height': '100vh', 'width': '100vw'}
)

def prepare_data(bond):
    bond['datetime'] = pd.to_datetime(bond['datetime'])
    bond['rptd_pr'] = bond['rptd_pr'].astype(float)
    bond['entrd_vol_qt'] = bond['entrd_vol_qt'].astype(float)
    bond['index'] = bond['index'].astype(int)

def order_type_handler(ot):
    # ['b','s']
    names = ['Dealer Buy', 'Dealer Sell', 'Inter-Dealer']
    colors = ['rgb(30, 201, 0)', 'rgb(229, 0, 0)','rgb(18, 117, 199)']

    nams = [] ; cols = []
    for t in ot:
        if t == 'B':
            nams.append(names[0])
            cols.append(colors[0])
        if t == 'S':
            nams.append(names[1])
            cols.append(colors[1])
        if t == 'D':
            nams.append(names[2])
            cols.append(colors[2])
    return nams, cols
    
# callbacks for scatter plot interaction and data selection 
@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('order-type', 'value'),
    Input('indicator-graphic', 'config'),
    Input('confirm-button','n_clicks')])
def update_graph(order_type, config, conf_button):
    
    # control flow for end of survey
    if conf_button < len(unique_cusips):
 
        if conf_button == None:
            conf_button = 0
        
        # allows for survey taker to loop through.
        click_tracker = conf_button 
        if click_tracker < 0:
            click_tracker = len(unique_cusips) + click_tracker

        # querying bond from database hosted on heroku
        cusip_id = unique_cusips[click_tracker]
        query = """SELECT * FROM trace_lean WHERE cusip_id = '{}' """.format(cusip_id)
        bond = pd.read_sql_query(query, connection)
        # making necesary type conversions
        prepare_data(bond)
         
        # dealing with differnt types of bond order types for radio button customization
        type_info = order_type_handler(order_type)
        names = type_info[0]
        colors = type_info[1]

        return {
            'data': [go.Scattergl(
                    x = bond[bond['rpt_side_cd'] == order_type[i]]['datetime'],
                    y = bond[bond['rpt_side_cd'] == order_type[i]]['rptd_pr'],
                    text = bond[bond['rpt_side_cd'] == order_type[i]]['entrd_vol_qt'],
                    name = names[i],
                    mode = 'markers',
                    opacity = 1,
                    marker = {
                        'size': 7,
                        'color': colors[i],
                        'line': {'width': 0.5, 'color': 'white'}
                        },) for i in range(len(order_type))],
            'layout': go.Layout(
                    title='TRACE Outlier Classification | Completed: {}'.format(click_tracker),
                    margin={'l': 50, 'b': 50, 't': 80, 'r': 80},
                    # note the +- 5 is to handle with prices near 0
                    yaxis={'title':'Prices', 'range': [bond['rptd_pr'].min()*.75-5, bond['rptd_pr'].max()*1.25+5]},
                    legend={'x': 1, 'y': 1},
                    hovermode='closest',
                    clickmode = 'event+select'
                    )
        }
            
# function that helps convert data from string into python objects. Storing data in HTML div
def default(o):
    if isinstance(o, np.int32): 
        return int(o)  
    else:
        raise TypeError
 
@app.callback(
    [Output('index-log','children'), 
    Output('codex-index','children'),
    Output('data-table','children')],
    [Input('indicator-graphic','selectedData'),
    Input('confirm-button','n_clicks'),
    Input('tabs','value')],
    [State('hidden','children'),
    State('index-log','children'),
    State('dump','children')]
)
def update_table(selected_data, conf_button, tab, hidden, current, prev_inds):
 
    if prev_inds == None:
        PREV = []
    else:
        prev_inds = json.loads(prev_inds)
        PREV = prev_inds['inds']

    if conf_button < len(unique_cusips):
             
        if selected_data != None:

            if selected_data['points'] != []:
             
                # type manipulation for prev/next functionality
                if conf_button == None:
                    conf_button = 0
                click_tracker = conf_button 

                cusip_id = unique_cusips[click_tracker]
                query = """SELECT * FROM trace_lean WHERE cusip_id = '{}' """.format(cusip_id)
                bond = pd.read_sql_query(query, connection)
                # making necesary type conversions
                prepare_data(bond)
                 
                # mapping pointNumber to index of global DataFrame
                buy = bond[bond['rpt_side_cd'] == 'B']
                sell = bond[bond['rpt_side_cd'] == 'S']
                D = bond[bond['rpt_side_cd'] == 'D']
 
                fig_data = pd.DataFrame(selected_data["points"])[['curveNumber','pointNumber','y','text']]

                hidden = json.loads(hidden)
                _B_ = hidden['buy']
                _S_ = hidden['sell']
                _D_ = hidden['D']
 
                curve_buy = fig_data[(fig_data['curveNumber'] == 0) & ((fig_data['pointNumber']).isin(_B_) == False)]
                curve_sell = fig_data[(fig_data['curveNumber'] == 1) & ((fig_data['pointNumber']).isin(_S_) == False)]
                curve_D = fig_data[(fig_data['curveNumber'] == 2) & ((fig_data['pointNumber']).isin(_D_) == False)]

                if max(list(curve_buy['pointNumber'])+[-1]) < len(buy) and \
                    max(list(curve_sell['pointNumber'])+[-1]) < len(sell) and \
                    max(list(curve_D['pointNumber'])+[-1]) < len(D):

                    # collecting indicies 
                    b = list(buy.iloc[curve_buy['pointNumber']]['index'])
                    s = list(sell.iloc[curve_sell['pointNumber']]['index'])   
                    d = list(D.iloc[curve_D['pointNumber']]['index'])   
                    indicies = b+s+d
 
                    # manipulation for dataTable format
                    DT = bond[(bond['index']).isin(indicies)]
                    DT['Datetime'] = DT['datetime']
                    DT['Price'] = DT['rptd_pr']
                    DT['Volume'] = DT['entrd_vol_qt']
                    DT['B/S/ID'] = DT['rpt_side_cd']
                    DT = DT[['Datetime','Price','Volume','B/S/ID']]

                    # returning dataTable
                    return [
                        json.dumps( \
                        {'buy': curve_buy['pointNumber'].tolist(), \
                        'sell': curve_sell['pointNumber'].tolist(), \
                        'D': curve_D['pointNumber'].tolist()}, default = default), \

                        json.dumps({'inds':indicies}, default = default), \

                        dash_table.DataTable( \
                            id = 'a-table', \
                            columns = [{"name": i, "id": i} for i in DT.columns], \
                            data = DT.to_dict("rows"), \
                            style_cell = {'textAlign': 'center','padding': '5px'}, \
                            style_as_list_view = True, \
                            style_cell_conditional=[ \
                                {'if': {'column_id': 'Datetime'},'width': '100px'}, \
                                {'if': {'column_id': 'Price'},'width': '100px'}, \
                                {'if': {'column_id': 'Volume'},'width': '100px'}], \
                            style_header = {'backgroundColor': 'white', 'fontWeight': 'bold'}, \
                            fixed_rows={'headers': True, 'data': 0 },
                            page_size= 10,
                            style_table={ \
                                'height': '20vh', 'width': '50vw', 'maxHeight': '300px', \
                                'maxWidth': '500px',"margin-left": "auto", "margin-right": "auto"})
                        
                        ]
                else:
                    return [json.dumps({'buy': [], 'sell': [], 'D': []}), json.dumps({'inds': PREV}, default=default),'']
            else:
                return [json.dumps({'buy': [], 'sell': [], 'D': []}), json.dumps({'inds': PREV}, default=default),'']
        else:
            return [json.dumps({'buy': [], 'sell': [], 'D': []}), json.dumps({'inds': PREV}, default=default),'']
    else:
        return [json.dumps({'buy': [], 'sell': [], 'D': []}), json.dumps({'inds': PREV}, default=default),'']
 
# upon tranition to next timeseries/bond - store data in page, keeps track of 
# indicies from official survey DB used to optimize filter 
@app.callback(
    [Output('indicator-graphic','selectedData'),
    Output('hidden','children'),
    Output('dump','children'),
    Output('formatted','children'),
    Output('order-type','value')],
    [Input('confirm-button','n_clicks'),
    Input('finish-surv','submit_n_clicks')
    ],
    [State('index-log','children'),
    State('hidden','children'),
    State('codex-index','children'),
    State('dump','children'),
    State('name','value'),
    State('organization','value'),
    State('professional-experience','value'),
    State('bond-experience','value')]
)
def data_handler(clicks, yeet, child, hidden, codex, dump, name, organization, pro_exp, bond_exp):

    if codex == None:
        codex = json.dumps({'inds': []}, default=default)
    if dump == None:
        dump = json.dumps({'inds': []}, default=default)

    new_inds = json.loads(codex)['inds']      

    update_statement = """ 
        UPDATE survey_data
        SET indicies = array_cat(indicies, %s) 
        WHERE username = %s and organization = %s """
        
    record_to_update = (str(new_inds).replace('[','{').replace(']','}'), name, organization)
    cursor.execute(update_statement, record_to_update)
    connection.commit()
        
    if codex == None and dump == None:
        _Codex_ = []
    else:
        codex = json.loads(codex)
        dump = json.loads(dump)
        _Codex_ = list(set(codex['inds'] + dump['inds']))

    if child != None and hidden != None:
        # merging previously selected to current CUSIP
        child = json.loads(child)
        B1 = child['buy']
        S1 = child['sell']
        D1 = child['D']
        hidden = json.loads(hidden)
        B2 = hidden['buy']
        S2 = hidden['sell']
        D2 = hidden['D']
        B = B1 + B2
        S = S1 + S2 
        D = D1 + D2
        return [{"points": []}, json.dumps({'buy': B, 'sell': S, 'D': D}), json.dumps({'inds': _Codex_}, default=default), '{}', ['B', 'S', 'D']]
    else:
        return [{"points": []}, json.dumps({'buy': [], 'sell': [], 'D': []}), json.dumps({'inds': _Codex_}, default=default), '{}', ['B', 'S', 'D']]

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
        
        indicies = []
        insert_statement = """ INSERT INTO survey_data (username, organization, pro_exp, bond_exp, indicies) VALUES (%s,%s,%s,%s,%s)"""
        record_to_insert = (name, organization, pro_exp, bond_exp, indicies)
        cursor.execute(insert_statement, record_to_insert)
        connection.commit()
     
        return user_information
    else:
        return ''

# Tab transition/toggling 
@app.callback(
    [Output('tab1','disabled'),
    Output('tab2','disabled'),
    Output('tab3','disabled'),
    Output('tabs','value')],
    [Input('begin-survey','submit_n_clicks'),
    Input('confirm-button','n_clicks'),
    Input('finish-surv','submit_n_clicks')]
)
def next_tab1(begin_clicks, conf_clicks, finish):

    # finish survey early
    if finish == 1:
        conf_clicks = len(unique_cusips)

    # tab management
    if begin_clicks != 1:
        return [False,True,True,'tab1']
    elif begin_clicks == 1 and conf_clicks != len(unique_cusips):
        return [True, False, True,'tab2']
    elif conf_clicks == len(unique_cusips):
        return [True,True, False,'tab3']

# sending feedback to database 
@app.callback(
    Output('feedback-hidden','children'),
    [Input('end','n_clicks')],
    [State('feedback', 'value'),
    State('name','value'),
    State('organization','value')]
)
def send_feedback(n_clicks, feedback, user, organization):

    if n_clicks == 1:
        
        update_statement = """ UPDATE survey_data SET feedback = %s WHERE username = %s and organization = %s"""
        record_to_update = (feedback, user, organization)
        cursor.execute(update_statement, record_to_update)
        connection.commit()
        return None
 
if __name__ == '__main__':
    app.run_server(debug=True)
 
