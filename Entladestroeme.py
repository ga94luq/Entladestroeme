from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

chart_types = [
    {'label': 'Scatter Plot', 'value': 'scatter'},
    {'label': 'Bar Chart', 'value': 'bar'}
]

df_1 = pd.read_csv('https://raw.githubusercontent.com/ga94luq/Entladestroeme/main/Entladestroeme_VD.csv')
df_2 = pd.read_csv('https://raw.githubusercontent.com/ga94luq/Entladestroeme/main/Entladestroeme_VH.csv')
df = pd.concat([df_1, df_2], ignore_index=True)

df['Typ'] = df['Typ'].replace(1.0, 'VH')
df['Typ'] = df['Typ'].replace(2.0, 'VD')
df['Bezeichnung'] = 'SOC:' + df['SOC'].astype(str) + '% SiO:' + df['SiO'].astype(str) + '% D:' + df['D'].astype(str) + df['Typ']
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
        html.H6("Überschrift festlegen"),
        dcc.Input(
            id='title-input',
            type='text',
            value='Auswertung',
            style={'width': '50%'}
        ),
    ]),
    dcc.Dropdown(
        id='chart-type-dropdown',
        options=[
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Line Plot', 'value': 'line'},
            {'label': 'Bar Chart', 'value': 'bar'}
        ],
        value='line',
        clearable=False
    ),
    dcc.Graph(id="chart-graph"),
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
        html.H6("Typ auswählen"),
        dcc.Checklist(
            id='typ-checklist',
            options=[
                {'label': 'VH', 'value': 'VH'},
                {'label': 'VD', 'value': 'VD'}
            ],
            value=['VH', 'VD'],
            labelStyle={'display': 'block'}
        ),
    ]),
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
        html.H6("X-Achsenbeschriftung"),
        dcc.Input(
            id='x-axis-label',
            type='text',
            value='Zeit',
            style={'width': '50%'}
        ),
    ]),
    html.Div([
        html.H6("Y-Achsenbeschriftung"),
        dcc.Input(
            id='y-axis-label',
            type='text',
            value='Current',
            style={'width': '50%'}
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
        dcc.Dropdown(
            id='Y_Achsen',
            options=dropdown_options,
            multi=True,
            value=['Current'],
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
            value=[ 15],
            labelStyle={'display': 'block'}
        ),
    ]),
    html.Div([
        html.H6("Werte für Bezeichnung auswählen"),
        dcc.Checklist(
            id='bezeichnung-checklist',
            options=[{'label': label, 'value': label} for label in df['Bezeichnung'].unique()],
            value=[],
            labelStyle={'display': 'block'}
        ),
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
])

@app.callback(
    [Output("chart-graph", "figure"),
     Output("range-slider-y", "min"),
     Output("range-slider-y", "max"),
     Output("range-slider-y", "marks"),
     Output('bezeichnung-checklist', 'value'),
     Output('bezeichnung-checklist', 'options')],
    [Input('typ-checklist', 'value'),
     Input("range-slider-x", "value"),
     Input("range-slider-y", "value"),
     Input('x-axis-dropdown', 'value'),
     Input('Y_Achsen', 'value'),
     Input('color-dropdown', 'value'),
     Input('symbol-dropdown', 'value'),
     Input('soc-checklist', 'value'),
     Input('sio-checklist', 'value'),
     Input('chart-type-dropdown', 'value'),
     Input('bezeichnung-checklist', 'value'),
     Input('x-axis-label', 'value'),
     Input('y-axis-label', 'value'),
     Input('title-input', 'value'),
     Input('marker-radio', 'value')]
)
def update_bar_chart(typ_check, x_range, y_range, x_column, y_columns, color_column, symbol_column, soc_values, sio_values,
                     chart_type, bezeichnung_values, x_axis_label, y_axis_label, title, show_markers):
    df = data

    df_1 = df[df['SOC'].isin(soc_values) & df['SiO'].isin(sio_values) & df['Typ'].isin(typ_check)]

    Bez_values = df_1['Bezeichnung'].unique()

    Min = 0
    Max = 0

    for col in y_columns:
        if df[col].min() < Min:
            Min = df[col].min()
            Min_col = col
        if df[col].max() > Max:
            Max = df[col].max()
            Max_col = col

    min_y = df[y_columns].min().min()
    LowerGrenze = math.floor(min_y / 10.0) * 10
    max_y = df[y_columns].max().max()
    UpperGrenze = math.ceil(max_y / 10) * 10

    low_x, high_x = x_range
    low_y, high_y = y_range

    mask_x = (df['D'] >= low_x) & (df['D'] <= high_x)
    mask_y = (df[y_columns] >= low_y) & (df[y_columns] <= high_y)
    for col in y_columns:
        mask_y = (df[col] >= low_y) & (df[col] <= high_y)

    if len(y_columns) < 2 and y_columns[0] == 'Current':
        df = df[
            df['SOC'].isin(soc_values) & df['SiO'].isin(sio_values) & df['Bezeichnung'].isin(bezeichnung_values) & df[
                'Typ'].isin(typ_check) & mask_y]
    else:
        df = df[df['SOC'].isin(soc_values) & df['SiO'].isin(sio_values) & df['Bezeichnung'].isin(bezeichnung_values) & df[
                'Typ'].isin(typ_check) & mask_y]

    df[color_column] = df[color_column].astype(str)

    step_size = 10
    NumberofSteps = int((UpperGrenze - LowerGrenze) / step_size) + 1
    marks = {LowerGrenze + i * step_size: str(round(LowerGrenze + i * step_size, 2)) for i in range(NumberofSteps)}

    if len(y_columns) == 1:
        if chart_type == 'line':
            if not show_markers:
                fig = px.line(
                    df[mask_x & mask_y], x=x_column, y=y_columns[0],
                    color=color_column,
                    hover_data=['Bezeichnung'], width=2000, height=800)
            else:
                fig = px.line(
                    df[mask_x & mask_y], x=x_column, y=y_columns[0],
                    color=color_column, markers=True, symbol=symbol_column,
                    hover_data=['Bezeichnung'], width=2000, height=800)


        elif chart_type == 'bar':
            fig = px.bar(
                df[mask_x & mask_y],
                x=x_column,
                y=y_columns[0],
                color=color_column,
                hover_data=['Bezeichnung'],
                width=2000,
                height=800,
            )
        elif chart_type == 'scatter':
            fig = px.scatter(
                df[mask_x & mask_y],
                x=x_column,
                y=y_columns[0],
                color=color_column,
                symbol=symbol_column,
                hover_data=['Bezeichnung'],
                width=2000,
                height=800,
            )
        fig.update_xaxes(title=x_axis_label, rangeslider_visible=True)
        fig.update_yaxes(title=y_axis_label)
    else:
        fig = make_subplots(rows=1, cols=len(y_columns))
        i = 0
        if chart_type == 'line':
            for col in y_columns:
                i += 1
                for Bez in bezeichnung_values:
                    fig.add_trace(go.Scatter(
                        x=df[x_column],
                        y=df.loc[df['Bezeichnung'] == Bez, col],
                        name=col + ' ' + Bez,
                        mode='lines+markers' if show_markers else 'lines'),
                        row=1,
                        col=i)
        elif chart_type == 'bar':
            for col in y_columns:
                i += 1
                for Bez in bezeichnung_values:
                    fig.add_trace(go.Bar(
                        x=df[x_column],
                        y=df[col],
                        name=col + ' ' + Bez),
                        row=1,
                        col=i)
        elif chart_type == 'scatter':
            for col in y_columns:
                i += 1
                for Bez in bezeichnung_values:
                    fig.add_trace(go.Scatter(
                        x=df[x_column],
                        y=df[col],
                        name=col + ' ' + Bez,
                        mode='markers',
                        marker_symbol=df[symbol_column]),
                        row=1,
                        col=i)

    large_rockwell_template = dict(
        layout=go.Layout(
            title_font=dict(family="Arial", size=24),
            xaxis=dict(showline=True, zeroline=False, linecolor='black'),
            yaxis=dict(showline=True, zeroline=False, linecolor='black'),
            plot_bgcolor='white',
        )
    )
    fig.update_layout(template=large_rockwell_template)
    fig.update_layout(title=title)
    return fig, LowerGrenze, UpperGrenze, marks, bezeichnung_values, [{'label': label, 'value': label} for label in
                                                                      Bez_values]


if __name__ == '__main__':
    app.run_server(debug=True)
