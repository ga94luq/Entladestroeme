from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import math
import plotly.graph_objects as go
from scipy.signal import savgol_filter

chart_types = [
    {'label': 'Scatter Plot', 'value': 'scatter'},
    {'label': 'Bar Chart', 'value': 'bar'}
]

df_VD = pd.read_csv('https://raw.githubusercontent.com/ga94luq/Entladestroeme/main/Entladestroeme_VD.csv')
df_VH = pd.read_csv('https://raw.githubusercontent.com/ga94luq/Entladestroeme/main/Entladestroeme_VH.csv')

df = pd.concat([df_VD, df_VH], ignore_index=True)
df = df.reset_index(drop=True)

df['Typ'] = df['Typ'].replace(1.0, 'VH')
df['Typ'] = df['Typ'].replace(2.0, 'VD')
df['Bezeichnung'] = 'SOC:' + df['SOC'].astype(str) + '% SiO:' + df['SiO'].astype(str) + '% D:' + df['D'].astype(str)

data = df

app = Dash(__name__)
server = app.server

dropdown_options = [{'label': col, 'value': col} for col in df.columns]

initial_min_y = df['Current'].min()
LowerGrenze = math.ceil(initial_min_y / 10.0) * 10
initial_max_y = df['Current'].max()
UpperGrenze = math.ceil(initial_max_y / 10) * 10
app.layout = html.Div(style={'backgroundColor': 'white'}, children=[
    html.H4('Auswertungstool'),
    html.Div([
        html.H6("Combination"),
        html.Div([
            html.H6("Achsenbeschriftung ändern"),
            dcc.Input(id="x-axis-title", type="text", placeholder="X-Achsenbeschriftung"),
            dcc.Input(id="y-axis-title", type="text", placeholder="Y-Achsenbeschriftung"),
            dcc.Input(id="title", type="text", placeholder="Titel des Plots"),
            html.Button(id="submit-title", n_clicks=0, children="Titel anwenden"),
        ]),
        html.Div([
            html.H6("Marker anzeigen"),
            dcc.RadioItems(
                id='marker-radio',
                options=[
                    {'label': 'Ja', 'value': True},
                    {'label': 'Nein', 'value': False}
                ],
                value=False,
                labelStyle={'display': 'block'}
            ),
        ]),
    ]),
    html.Div([
        dcc.Graph(id='graph1', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='graph2', style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    ]),
    html.Div([
        html.Label('Übergang'),
        dcc.Slider(
            id='Uebergang',
            min=0,
            max=df['Zeit'].max(),
            value=500,
        ),
    ]),
    dcc.Graph(id='graph3'),
    html.P("Auswahl der Durchläufe"),
    dcc.RangeSlider(
        id='range-slider-x',
        min=1, max=5, step=1,
        marks={i: str(i) for i in range(1, 6)},
        value=[1, 5],
        className='slider-x',
        tooltip={"placement": "bottom", "always_visible": False}
    ),
    html.Div([
        html.H6("Y-Achsenbereich"),
        dcc.RangeSlider(
            id='range-slider-y',
            min=initial_min_y,
            max=initial_max_y,
            step=0.05,
            marks={LowerGrenze: str(LowerGrenze), UpperGrenze: str(UpperGrenze)},
            value=[initial_min_y, initial_max_y],
            className='slider-y',
            tooltip={"placement": "bottom", "always_visible": True}
        ),
    ]),
    html.Div([
        html.H6("Spaltenauswahl"),
        dcc.Dropdown(
            id='x-axis-dropdown',
            options=dropdown_options,
            value='Zeit',
            clearable=False
        ),
    ]),
    html.Div([
        html.H6("Farbauswahl"),
        dcc.Dropdown(
            id='color-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns],
            value='Bezeichnung',
            clearable=False
        ),
    ]),
    html.Div([
        html.H6("Symbolauswahl"),
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns],
            value='SiO',
            clearable=False
        ),
    ]),
    html.Div([
        html.H6("Werte für SOC auswählen"),
        dcc.Checklist(
            id='soc-checklist',
            options=[
                {'label': '10%', 'value': 10},
                {'label': '30%', 'value': 30},
                {'label': '50%', 'value': 50},
                {'label': '70%', 'value': 70},
                {'label': '90%', 'value': 90}
            ],
            value=[50],
            labelStyle={'display': 'block'}
        ),
    ]),
    html.Div([
        html.H6("Werte für SiO auswählen"),
        dcc.Checklist(
            id='sio-checklist',
            options=[
                {'label': '0%', 'value': 0},
                {'label': '10%', 'value': 10},
                {'label': '15%', 'value': 15}
            ],
            value=[15],
            labelStyle={'display': 'block'}
        ),
    ]),
    html.Div([
        html.H6("Werte für Bezeichnung auswählen"),
        dcc.Checklist(
            id='bezeichnung-checklist',
            options=[{'label': label, 'value': label} for label in df['Bezeichnung'].unique()],
            value=['SOC:50% SiO:15% D:1'],
            labelStyle={'display': 'block'}
        ),
    ]),
])


@app.callback(
    [Output("graph1", "figure"),
     Output("graph2", "figure"),
     Output("graph3", "figure"),
     Output("range-slider-y", "min"),
     Output("range-slider-y", "max"),
     Output("range-slider-y", "marks"),
     Output('bezeichnung-checklist', 'options'),
     Output('bezeichnung-checklist', 'value')],
    [Input("range-slider-x", "value"),
     Input("range-slider-y", "value"),
     Input('x-axis-dropdown', 'value'),
     Input('color-dropdown', 'value'),
     Input('symbol-dropdown', 'value'),
     Input('soc-checklist', 'value'),
     Input('sio-checklist', 'value'),
     Input('bezeichnung-checklist', 'value'),
     Input('x-axis-title', 'value'),
     Input('y-axis-title', 'value'),
     Input('title', 'value'),
     Input('marker-radio', 'value'),
     Input('Uebergang', 'value')]
)
def update_bar_chart(x_range, y_range, x_column, color_column, symbol_column, soc_values, sio_values,
                      bezeichnung_values, xAchse_Label, yAchse_Label, title, show_markers, Uebergang):
    df = data
    df_1 = df[df['SOC'].isin(soc_values) & df['SiO'].isin(sio_values) ]
    Bez_values = df_1['Bezeichnung'].unique()

    min_y = df['Current'].min().min()
    LowerGrenze = math.floor(min_y / 10.0) * 10
    max_y = df['Current'].max().max()
    UpperGrenze = math.ceil(max_y / 10) * 10

    low_x, high_x = x_range
    low_y, high_y = y_range

    mask_x = (df['D'] >= low_x) & (df['D'] <= high_x)
    mask_y = (df['Current'] >= low_y) & (df['Current'] <= high_y)

    df = df[df['SOC'].isin(soc_values) & df['SiO'].isin(sio_values) & df['Bezeichnung'].isin(bezeichnung_values) & mask_y]

    df[color_column] = df[color_column].astype(str)

    step_size = 10
    NumberofSteps = int((UpperGrenze - LowerGrenze) / step_size) + 1
    marks = {LowerGrenze + i * step_size: str(round(LowerGrenze + i * step_size, 2)) for i in range(NumberofSteps)}


    fig = go.Figure()
    try:
        # Maske für 'VD'
        mask_VD = (df['Typ'] == 'VD')
        # Maske für 'VH'
        mask_VH = (df['Typ'] == 'VH')

        V1 = df[mask_x & mask_y & mask_VD & (df['Zeit'] <= Uebergang)]['Current']
        V1_Zeit = df[mask_x & mask_y & mask_VD & (df['Zeit'] <= Uebergang)]['Zeit']
        V2 = df[mask_x & mask_y & mask_VH & (df['Zeit'] > Uebergang)]['Current']
        V2_Zeit = df[mask_x & mask_y & mask_VH & (df['Zeit'] > Uebergang)]['Zeit']
        # Kombinieren von V1 und V2
        V3 = pd.concat([V1, V2], ignore_index=True)
        V3_Zeit = pd.concat([V1_Zeit, V2_Zeit], ignore_index=True)
        # Glättung mit Savitzky-Golay-Filter
        window_size = 17
        poly_order = 9
        V3 = savgol_filter(V3, window_size, poly_order)

        fig.add_trace(go.Scatter(x= V3_Zeit,
                                 y=V3,
                                 #mode='Marker',
                                 name='Smoothed Signal'))
    except:
        print('Fehler')
        pass

    fig.add_trace(go.Scatter(
        x=df[mask_x & mask_y & (df['Typ'] == 'VD') & (df['Zeit'] <= Uebergang)][x_column],
        y=df[mask_x & mask_y & (df['Typ'] == 'VD') & (df['Zeit'] <= Uebergang)]['Current'],
        mode='lines',
        name='VD'
    ))

    fig.add_trace(go.Scatter(
        x=df[mask_x & mask_y & (df['Typ'] == 'VH') & (df['Zeit'] >= Uebergang)][x_column],
        y=df[mask_x & mask_y & (df['Typ'] == 'VH') & (df['Zeit'] >= Uebergang)]['Current'],
        mode='lines',
        name='VH'
    ))

    fig.update_layout(title='Mehrere Linien in einem Plot', xaxis_title='X-Achse', yaxis_title='Y-Achse')

    fig_VD = px.line(
        df[mask_x & mask_y & (df['Typ'] == 'VD')], x=x_column, y='Current',
        color=color_column,  # markers=show_markers, symbol=symbol_column,
        hover_data=['Bezeichnung']  # , width=2000, height=800
    )
    fig_VH= px.line(
        df[mask_x & mask_y & (df['Typ']=='VH')], x=x_column, y='Current',
        color=color_column, #markers=show_markers, symbol=symbol_column,
        hover_data=['Bezeichnung']#, width=2000, height=800
    )

    large_rockwell_template = dict(
        layout=go.Layout(
            title_font=dict(family="Arial", size=24),
            xaxis=dict(showline=True, zeroline=False, linecolor='black'),
            yaxis=dict(showline=True, zeroline=False, linecolor='black'),
            plot_bgcolor='white',
        )
    )
    fig.update_layout(template=large_rockwell_template)

    fig_VH.update_layout(template=large_rockwell_template)
    fig_VD.update_layout(template=large_rockwell_template)
    if yAchse_Label:
        fig.update_yaxes(title=yAchse_Label)
    if xAchse_Label:
        fig.update_xaxes(title=xAchse_Label)
    if title:
        fig.update_layout(title=title)

    return fig_VD, fig_VH, fig, LowerGrenze, UpperGrenze, marks, [{'label': label, 'value': label} for label in Bez_values], bezeichnung_values


if __name__ == '__main__':
    app.run_server(debug=True)
