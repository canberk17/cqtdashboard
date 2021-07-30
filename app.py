import datetime
import requests

import pathlib
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output, State
from plotly import tools
import time
import dash_table


def fig1(df_nested):
    colors = {
        'background': 'black',
        'text': '#FFFFFF'
    }

    today = datetime.datetime.today().strftime("%Y -%m -%d")
    df_nested
    df = df_nested.loc[df_nested['timestamp'] >= today].groupby(
        ['contract_name', 'contract_ticker_symbol']).mean('close.quote').reset_index()

    fig = px.pie(df, values='close.quote', names='contract_name', labels={"contract_name": 'Contract Name',
                                                                          "close.quote": "USD Value"}, title='Asset Allocation', color_discrete_sequence=["#ff4c8b", "#00d8d5", '#f7f7f7'])
    fig.update_traces(textposition='inside')
    # fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text']
                      )

    fig.add_layout_image(
        dict(
            source="assets/CQT.svg",
            xref="paper", yref="paper",
            x=0.5, y=0.24,
            sizex=0.5, sizey=0.6,
            xanchor="center", yanchor="bottom"
        )
    )

    fig.add_layout_image(
        dict(
            source="assets/aa_footer.svg",
            xref="paper", yref="paper",
            x=0.7, y=(-0.20),
            sizex=1.7, sizey=.8,
            xanchor="center", yanchor="bottom"
        )
    )

    return fig


def lunar_sentiment(data):
    today = datetime.datetime.today().strftime("%Y -%m -%d")
    df = data.loc[data['timestamp'] >= today].groupby(
        ['contract_name', 'contract_ticker_symbol']).mean('close.quote').reset_index()
    ltick = []
    lsent = []
    for ticker in df['contract_ticker_symbol']:

        try:
            lc_response = requests.get(
                f"https://api.lunarcrush.com/v2?data=assets&key=olr3cu6lnc897ezr37jpo&symbol={ticker}&time_series_indicators=average_sentiment&data_points=0").json()
            ltick.append(lc_response['data'][0]['symbol'])
            lsent.append(lc_response['data'][0]['average_sentiment'])
        except:
            pass

    dic = {'Symbol': ltick,
           'Average Public Sentiment': lsent}

    df = pd.DataFrame.from_dict(dic)
    return df


def total_value(data):
    today = datetime.datetime.today().strftime("%Y -%m -%d")
    df = data.loc[data['timestamp'] >= today].groupby(
        ['contract_name', 'contract_ticker_symbol']).mean('close.quote').reset_index()

    return df['close.quote'].sum().round(2)


def fig2(df_nested):
    colors = {
        'background': 'black',
        'text': '#FFFFFF'
    }

    fig2 = px.line(df_nested, x="timestamp", y="close.quote", color="contract_name", color_discrete_sequence=["#ff4c8b", "#00d8d5", '#f7f7f7'], line_group="contract_ticker_symbol", labels={
        "contract_name": 'Contract Name',
        "timestamp": "Date",
                     "close.quote": "USD Value",
                     "contract_ticker_symbol": "Ticker"
    }, title='Asset Value Over Time', hover_name="contract_ticker_symbol")
    fig2.update_layout(plot_bgcolor=colors['background'],
                       paper_bgcolor=colors['background'], font_color=colors['text'])

    fig2.add_layout_image(
        dict(
            source="assets/CQT.svg",
            xref="paper", yref="paper",
            x=0.5, y=0.24,
            sizex=0.5, sizey=0.6,
            xanchor="center", yanchor="bottom"
        )
    )

    fig2.add_layout_image(
        dict(
            source="assets/aa_footer.svg",
            xref="paper", yref="paper",
            x=0.7, y=(-0.20),
            sizex=1.7, sizey=.8,
            xanchor="center", yanchor="bottom"
        )
    )
    return fig2


app = dash.Dash(
    __name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width"}],
)
app.title = ""

server = app.server

PATH = pathlib.Path(__file__).parent


# API Requests for news div
news_requests = requests.get(
    "https://newsapi.org/v2/everything?q=bitcoin&sources=bbc-news&apiKey=2a3f8518d0d2450a81858a811f84f02a"
)

# API Call to update news


def update_news():
    json_data = news_requests.json()["articles"]
    df = pd.DataFrame(json_data)
    df = pd.DataFrame(df[["title", "url"]])
    max_rows = 10
    return html.Div(
        children=[
            html.P(className="p-news", children="Headlines"),
            html.P(
                className="p-news float-right",
                children="Last update : "
                + datetime.datetime.now().strftime("%H:%M:%S"),
            ),
            html.Table(
                className="table-news",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.A(
                                        className="td-link",
                                        children=df.iloc[i]["title"],
                                        href=df.iloc[i]["url"],
                                        target="_blank",
                                    )
                                ]
                            )
                        ]
                    )
                    for i in range(min(len(df), max_rows))
                ],
            ),
        ]
    )


# Dash App Layout
app.layout = html.Div(
    className="row",
    children=[
        # Interval component for live clock
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),

        # Interval component for graph updates
        dcc.Interval(id="i_news", interval=1 * 60000, n_intervals=0),
        # Left Panel Div
        html.Div(
            className="three columns div-left-panel",
            children=[
                # Div for Left Panel App Info
                html.Div(
                    className="div-info",
                    children=[
                        html.Img(
                            className="logo", src=app.get_asset_url("CQT.svg")
                        ),
                        html.H6(className="title-header",
                                children="Covalent Analytics"),
                        html.P(
                            """
                            Covalent Analytics provides portfolio tracking services across chains
                            """
                        ),

                    ],
                ),


                # Div for News Headlines
                html.Div(
                    className="div-news",
                    children=[html.Div(id="news", children=update_news())],
                ),
            ],
        ),
        # Right Panel Div
        html.Div(
            className="nine columns div-right-panel",
            children=[


                # Panel for orders
                html.Div(
                    id="bottom_panel",
                    className="row div-bottom-panel",
                    children=[
                        html.Div(
                            className="display-inlineblock",
                            children=[
                                dcc.Input(
                                    id="address", placeholder="Enter wallet address...", type="text"),

                                dcc.Dropdown(id='chain_id',  options=[
                                    {"label": "Ethereum", "value": "1"},
                                    {"label": "Matic", "value": "137"},
                                    {"label": "Binance Smart Chain", "value": "56"},
                                    {"label": "Avalanche", "value": "43114"},
                                    {"label": "Fantom", "value": "250"}
                                ], placeholder="Select Chain",
                                    value=[],
                                    multi=True

                                ),


                            ],
                        ),
                        html.Div(
                            className="display-inlineblock float-right",
                            children=[
                                html.Button(
                                    'Add Wallet', id='btn-1', n_clicks=0)

                            ],
                        ),
                        dcc.Loading(
                            id="loading-1",
                            # color='#ff4c8b',
                            type="default",
                            children=html.Div(id="loading-output-1")
                        ),
                        # html.Div(id='container')

                    ],
                ),
            ],
        ),


    ],
)


def normalize(data):
    df = pd.json_normalize(data, record_path=['holdings'], meta=[
                           'contract_ticker_symbol', 'contract_name', "contract_address"])
    df = df[['contract_ticker_symbol', 'contract_name',
             "contract_address", 'timestamp', 'close.quote']]
    return df


def set_time(data):
    return pd.to_datetime(data['timestamp'])


@app.callback(Output("loading-output-1", "children"), Input("chain_id", "value"),
              Input("address", "value"),
              prevent_initial_call=True,)
def input_triggers_spinner(value, address):
    time.sleep(1)
    return display(value, address)


def display(value, address):

    ctx = dash.callback_context

    api_key = 'ckey_57eeb470248541708eeaf028c9d'

    if not ctx.triggered:
        pass

    else:
        lis = []
        if len(value) > 0:
            for i in value:

                chain_id = i
                address = address
                response = requests.get(
                    f"https://api.covalenthq.com/v1/{chain_id}/address/{address}/portfolio_v2/?format=format%3Dcsv&key={api_key}").json()['items']

                data = response
                data = normalize(data)
                data['timestamp'] = set_time(data)

                lis.append(
                    html.Div([

                        dcc.Graph(
                            id='graph1',
                            figure=fig1(data),
                            config={'displaylogo': False},
                            style={'display': 'inline-block'

                                   },



                        ),
                        html.Th(f" Total Valuation: {total_value(data)} $", className="display-inlineblock float-right"
                                ),


                        dash_table.DataTable(

                            columns=[{"name": i, "id": i}
                                     for i in lunar_sentiment(data).columns],
                            data=lunar_sentiment(data).to_dict('records'),
                            style_as_list_view=True,
                            style_header={
                                'backgroundColor': "#ff4c8b",
                                'color': '#f7f7f7',
                                'fontWeight': 'bold',
                                'textAlign': 'center',
                            },
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'lineHeight': '15px',
                                'textAlign': 'center',
                                'backgroundColor': 'black',
                                'padding': '5px',
                                'color': '#f7f7f7',
                            },
                        ),
                        dcc.Graph(
                            id='graph2',
                            figure=fig2(data),
                            config={'displaylogo': False},
                            style={'display': 'inline-block'},



                        ),


                    ])
                )

            return lis


# Callback to update news
@app.callback(Output("news", "children"), [Input("i_news", "n_intervals")])
def update_news_div(n):
    return update_news()


if __name__ == "__main__":
    app.run_server(debug=False)
